import React, { useState, useRef, useEffect } from "react";
import { toast } from "sonner";
import StreamingService from "../services/streamingService";
import type { AnnotatedFrameData } from "../services/streamingService";

interface SeamlessVideoStreamProps {
  onFrameSelected?: (
    frameData: string,
    detectionData: AnnotatedFrameData
  ) => void;
  onError?: (error: string) => void;
  confidenceThreshold?: number; // Threshold to auto-stop (default 0.8)
  autoStopDelay?: number; // Delay in ms before auto-stopping (default 1000)
}

const SeamlessVideoStream: React.FC<SeamlessVideoStreamProps> = ({
  onFrameSelected,
  onError,
  confidenceThreshold = 0.65,
}) => {
  const [isConnected, setIsConnected] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [currentFrame, setCurrentFrame] = useState<string>("");
  const [cleanFrame, setCleanFrame] = useState<string>(""); // Clean frame without annotations
  const [confidence, setConfidence] = useState(0);
  const [bestConfidence, setBestConfidence] = useState(0);
  const [frameCount, setFrameCount] = useState(0);
  const [isAutoStopping, setIsAutoStopping] = useState(false);
  const [debugMode, setDebugMode] = useState(false); // Enable debug mode by default

  // Robust confidence tracking
  const [confidenceHistory, setConfidenceHistory] = useState<number[]>([]);
  const [sustainedHighConfidence, setSustainedHighConfidence] = useState(false);
  const [highConfidenceStartTime, setHighConfidenceStartTime] = useState<
    number | null
  >(null);

  const videoRef = useRef<HTMLVideoElement>(null);
  const displayVideoRef = useRef<HTMLVideoElement>(null); // Separate video element for display
  const streamingServiceRef = useRef<StreamingService | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const autoStopTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    initializeStreamingService();
    return () => {
      cleanup();
    };
  }, []);

  // Ensure video element is available
  useEffect(() => {
    if (videoRef.current) {
      console.log("📹 Video element is available");
    }
  }, []);

  // Robust confidence tracking with sustained high confidence requirement
  useEffect(() => {
    // Update confidence history (keep last 100 frames)
    setConfidenceHistory((prev) => {
      const newHistory = [...prev, confidence];
      return newHistory.slice(-100); // Keep last 100 frames
    });

    // Check for sustained high confidence
    if (confidence >= confidenceThreshold && !isAutoStopping && isStreaming) {
      const now = Date.now();

      if (!highConfidenceStartTime) {
        // First time reaching high confidence
        setHighConfidenceStartTime(now);
        console.log(
          `🎯 High confidence started: ${confidence.toFixed(
            3
          )} >= ${confidenceThreshold}`
        );
      } else {
        // Check if we've maintained high confidence for 5 seconds
        const duration = now - highConfidenceStartTime;
        const requiredDuration = 5000; // 5 seconds

        if (duration >= requiredDuration && !sustainedHighConfidence) {
          console.log(
            `✅ Sustained high confidence for ${duration}ms, triggering auto-stop`
          );
          setSustainedHighConfidence(true);
          setIsAutoStopping(true);

          // Auto-stop after sustained high confidence
          autoStopTimeoutRef.current = setTimeout(() => {
            console.log(
              "🎯 Auto-stopping stream after sustained high confidence"
            );
            stopStreaming();

            // Use current frame (which should be the best one)
            if (currentFrame) {
              onFrameSelected?.(cleanFrame || currentFrame, {
                // Use clean frame if available, fallback to annotated
                annotated_frame: currentFrame,
                clean_frame: cleanFrame || currentFrame, // Use clean frame if available
                confidence,
                frame_number: frameCount,
                timestamp: frameCount / 30.0,
                detection_quality: {
                  brightness: 0,
                  contrast: 0,
                  face_count: 0,
                  body_count: 0,
                  landmark_count: 0,
                  total_confidence: confidence,
                },
                faces: [],
                bodies: [],
                eyes: [],
                pose_landmarks: [],
              });
              toast.success(
                "Perfect pose detected and captured automatically!"
              );
            }
          }, 2000); // 2 seconds after sustained confidence
        }
      }
    } else {
      // Reset if confidence drops below threshold
      if (highConfidenceStartTime) {
        console.log(
          `📉 Confidence dropped below threshold: ${confidence.toFixed(
            3
          )} < ${confidenceThreshold}`
        );
        setHighConfidenceStartTime(null);
        setSustainedHighConfidence(false);
      }
    }
  }, [
    confidence,
    confidenceThreshold,
    isAutoStopping,
    isStreaming,
    currentFrame,
    frameCount,
    onFrameSelected,
    highConfidenceStartTime,
    sustainedHighConfidence,
  ]);

  const initializeStreamingService = async () => {
    try {
      const service = new StreamingService();

      // Set up event handlers
      service.setOnConnected(() => {
        console.log("✅ Connected to streaming service");
        setIsConnected(true);
      });

      service.setOnDisconnected(() => {
        console.log("❌ Disconnected from streaming service");
        setIsConnected(false);
        setIsStreaming(false);
      });

      service.setOnStreamStarted(() => {
        console.log("🎥 Stream started");
        setIsStreaming(true);
        setFrameCount(0);
        setBestConfidence(0);
        setIsAutoStopping(false);
      });

      service.setOnStreamStopped(() => {
        console.log("⏹️ Stream stopped");
        setIsStreaming(false);
        setIsAutoStopping(false);
      });

      service.setOnAnnotatedFrame((data: AnnotatedFrameData) => {
        console.log("📸 Received annotated frame:", {
          confidence: data.confidence,
          frameNumber: data.frame_number,
          hasFrame: !!data.annotated_frame,
          hasCleanFrame: !!data.clean_frame,
        });

        setCurrentFrame(data.annotated_frame);
        setCleanFrame(data.clean_frame); // Store clean frame for try-on
        setConfidence(data.confidence);
        setFrameCount(data.frame_number);

        // Update best confidence
        if (data.confidence > bestConfidence) {
          setBestConfidence(data.confidence);
        }
      });

      service.setOnError((errorMsg: string) => {
        console.error("Streaming error:", errorMsg);
        toast.error(errorMsg);
        onError?.(errorMsg);
      });

      // Connect to backend
      await service.connect();
      streamingServiceRef.current = service;
    } catch (err) {
      console.error("Failed to initialize streaming service:", err);
      toast.error("Failed to connect to streaming service");
      onError?.("Failed to connect to streaming service");
    }
  };

  const startStreaming = async () => {
    try {
      if (!streamingServiceRef.current) {
        throw new Error("Streaming service not initialized");
      }

      // Get available video input devices
      const devices = await navigator.mediaDevices.enumerateDevices();
      const videoDevices = devices.filter(
        (device) => device.kind === "videoinput"
      );

      console.log("Available video devices:", videoDevices);

      // Use second camera if available, otherwise fall back to environment camera
      const videoConstraints: MediaTrackConstraints = {
        width: { ideal: 640 },
        height: { ideal: 480 },
      };

      if (videoDevices.length >= 2) {
        // Use the second camera (index 1)
        videoConstraints.deviceId = { exact: videoDevices[1].deviceId };
        console.log(
          "Using second camera:",
          videoDevices[1].label || "Camera 2"
        );
        toast.success(`Using camera: ${videoDevices[1].label || "Camera 2"}`);
      } else if (videoDevices.length === 1) {
        // Only one camera available, try environment facing (back camera)
        videoConstraints.facingMode = "environment";
        console.log("Only one camera found, trying environment facing");
        toast.info("Using back camera (environment facing)");
      } else {
        // Fallback to default user camera
        videoConstraints.facingMode = "user";
        console.log("No specific camera found, using default");
      }

      // Get camera access
      const stream = await navigator.mediaDevices.getUserMedia({
        video: videoConstraints,
        audio: false,
      });

      streamRef.current = stream;

      // Ensure video element exists
      if (!videoRef.current) {
        console.error(
          "❌ Video element not found - waiting for it to be available"
        );
        // Wait a bit for the video element to be rendered
        await new Promise((resolve) => setTimeout(resolve, 100));

        if (!videoRef.current) {
          throw new Error("Video element not found after waiting");
        }
      }

      console.log("🎥 Setting up video elements...");

      // Set up the main video element for frame capture
      videoRef.current.srcObject = stream;

      // Set up the display video element for showing original stream
      if (displayVideoRef.current) {
        displayVideoRef.current.srcObject = stream;
      }

      // Wait for video to be ready before starting frame capture
      await new Promise((resolve) => {
        videoRef.current!.onloadedmetadata = () => {
          console.log("🎥 Video metadata loaded, starting playback");
          videoRef.current!.play();

          // Also start the display video
          if (displayVideoRef.current) {
            displayVideoRef.current.play();
          }

          resolve(true);
        };
      });

      // Set video element in streaming service
      streamingServiceRef.current.setVideoElement(videoRef.current);
      console.log("✅ Video element set in streaming service");

      // Start streaming with stable settings
      streamingServiceRef.current.startStream({
        detection_mode: "realtime",
        confidence_threshold: confidenceThreshold,
        frame_rate: 10, // Lower frame rate for stability
      });

      // Simplified frame capture start
      setTimeout(() => {
        if (streamingServiceRef.current) {
          console.log("🚀 Starting frame capture...");
          streamingServiceRef.current.startFrameCapture();
        }
      }, 2000); // Simple 2-second delay
    } catch (err) {
      console.error("Failed to start streaming:", err);
      toast.error("Failed to start camera stream");
      onError?.("Failed to start camera stream");
    }
  };

  const stopStreaming = () => {
    try {
      // Clear auto-stop timeout
      if (autoStopTimeoutRef.current) {
        clearTimeout(autoStopTimeoutRef.current);
        autoStopTimeoutRef.current = null;
      }

      streamingServiceRef.current?.stopStream();

      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop());
        streamRef.current = null;
      }

      if (videoRef.current) {
        videoRef.current.srcObject = null;
      }
    } catch (err) {
      console.error("Failed to stop streaming:", err);
      toast.error("Failed to stop streaming");
    }
  };

  const cleanup = () => {
    stopStreaming();
    streamingServiceRef.current?.disconnect();
  };

  // Show only the backend annotated stream
  return (
    <div className="relative w-full h-full flex items-center justify-center bg-black">
      {/* Hidden video element for frame capture */}
      <video
        ref={videoRef}
        autoPlay
        muted
        playsInline
        className="hidden"
        onLoadedMetadata={() => {
          console.log("📹 Hidden video metadata loaded");
        }}
        onError={(e) => {
          console.error("Hidden video element error:", e);
          toast.error("Video element error");
        }}
      />

      {/* Main Video Display - Show both streams for debugging */}
      <div className="relative w-full h-full flex items-center justify-center">
        {currentFrame ? (
          debugMode ? (
            <div className="grid grid-cols-2 gap-4 w-full h-full p-4">
              {/* Original Camera Stream */}
              <div className="relative bg-black rounded-lg overflow-hidden">
                <video
                  ref={displayVideoRef}
                  autoPlay
                  muted
                  playsInline
                  className="w-full h-full object-contain"
                  onLoadedMetadata={() => {
                    console.log("📹 Display video metadata loaded");
                  }}
                  onError={(e) => {
                    console.error("Display video element error:", e);
                    toast.error("Display video element error");
                  }}
                />
                <div className="absolute top-2 left-2 bg-black bg-opacity-50 text-white px-2 py-1 rounded text-xs">
                  Original Stream
                </div>
              </div>

              {/* Backend Annotated Stream */}
              <div className="relative bg-black rounded-lg overflow-hidden">
                <img
                  src={currentFrame}
                  alt="Real-time body detection"
                  className="w-full h-full object-contain"
                  onError={(e) => {
                    console.error("Failed to load annotated frame:", e);
                    toast.error("Failed to display video stream");
                  }}
                />
                <div className="absolute top-2 left-2 bg-black bg-opacity-50 text-white px-2 py-1 rounded text-xs">
                  Backend Stream | Frame: {frameCount} | Conf:{" "}
                  {(confidence * 100).toFixed(0)}%
                </div>
              </div>
            </div>
          ) : (
            <div className="relative w-full h-full">
              <img
                src={currentFrame}
                alt="Real-time body detection"
                className="w-full h-full object-contain"
                onError={(e) => {
                  console.error("Failed to load annotated frame:", e);
                  toast.error("Failed to display video stream");
                }}
              />
              <div className="absolute top-2 left-2 bg-black bg-opacity-50 text-white px-2 py-1 rounded text-xs">
                Frame: {frameCount} | Conf: {(confidence * 100).toFixed(0)}%
              </div>
            </div>
          )
        ) : (
          <div className="relative w-full h-full">
            {/* Always render video element for camera access */}
            <video
              ref={displayVideoRef}
              autoPlay
              muted
              playsInline
              className="w-full h-full object-contain"
              onLoadedMetadata={() => {
                console.log("📹 Video metadata loaded");
              }}
              onError={(e) => {
                console.error("Video element error:", e);
                toast.error("Video element error");
              }}
            />

            {/* Overlay content based on state */}
            {!isStreaming ? (
              <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-50">
                <div className="text-white text-center">
                  <div className="text-6xl mb-4">📹</div>
                  <div className="text-xl mb-2">Camera Ready</div>
                  <div className="text-sm opacity-75">
                    Position yourself for body detection
                  </div>
                </div>
              </div>
            ) : (
              <div className="absolute top-2 left-2 bg-black bg-opacity-50 text-white px-2 py-1 rounded text-xs">
                Waiting for backend stream...
              </div>
            )}
          </div>
        )}

        {/* Start/Stop Button */}
        {!isStreaming && isConnected && (
          <button
            className="absolute bottom-8 left-1/2 transform -translate-x-1/2 bg-purple-600 hover:bg-purple-700 text-white font-semibold py-4 px-8 rounded-full transition-all duration-300 transform hover:scale-105 shadow-lg"
            onClick={startStreaming}
          >
            🎥 Start Detection
          </button>
        )}

        {isStreaming && !isAutoStopping && (
          <button
            className="absolute bottom-8 left-1/2 transform -translate-x-1/2 bg-red-600 hover:bg-red-700 text-white font-semibold py-3 px-6 rounded-full transition-all duration-300 transform hover:scale-105 shadow-lg"
            onClick={() => {
              stopStreaming();
              if (currentFrame) {
                onFrameSelected?.(cleanFrame || currentFrame, {
                  // Use clean frame if available
                  annotated_frame: currentFrame,
                  clean_frame: cleanFrame || currentFrame, // Use clean frame if available
                  confidence,
                  frame_number: frameCount,
                  timestamp: frameCount / 30.0,
                  detection_quality: {
                    brightness: 0,
                    contrast: 0,
                    face_count: 0,
                    body_count: 0,
                    landmark_count: 0,
                    total_confidence: confidence,
                  },
                  faces: [],
                  bodies: [],
                  eyes: [],
                  pose_landmarks: [],
                });
                toast.success("Frame selected manually!");
              }
            }}
          >
            ⏹️ Stop & Use Current Frame
          </button>
        )}

        {/* Auto-stopping indicator */}
        {isAutoStopping && (
          <div className="absolute top-4 left-1/2 transform -translate-x-1/2 bg-purple-600 text-white px-4 py-2 rounded-full text-sm font-medium">
            ✨ Perfect! Capturing your best pose...
          </div>
        )}

        {/* Debug toggle and information panel */}
        <div className="absolute top-4 right-4 flex flex-col gap-2">
          <button
            onClick={() => setDebugMode(!debugMode)}
            className="bg-purple-600 hover:bg-purple-700 text-white px-3 py-1 rounded text-xs font-medium"
          >
            {debugMode ? "🔧 Production Mode" : "🐛 Debug Mode"}
          </button>

          {isStreaming && (
            <div className="bg-black bg-opacity-75 text-white p-3 rounded-lg text-xs max-w-48">
              <div className="font-semibold mb-2">Debug Info</div>
              <div className="space-y-1">
                <div>
                  Status: {isAutoStopping ? "Auto-stopping" : "Streaming"}
                </div>
                <div>Confidence: {(confidence * 100).toFixed(1)}%</div>
                <div>Best: {(bestConfidence * 100).toFixed(1)}%</div>
                <div>Frames: {frameCount}</div>
                <div>Connected: {isConnected ? "Yes" : "No"}</div>
                <div>History: {confidenceHistory.length}/30</div>
                {highConfidenceStartTime && (
                  <div>
                    High Conf:{" "}
                    {Math.floor((Date.now() - highConfidenceStartTime) / 1000)}s
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SeamlessVideoStream;
