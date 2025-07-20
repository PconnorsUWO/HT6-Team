import React, { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  ArrowLeft,
  Camera,
  Sparkles,
  CheckCircle,
  AlertCircle,
  Home,
} from "lucide-react";
import { toast } from "sonner";
import StreamingService from "../services/streamingService";
import type {
  AnnotatedFrameData,
  DetectionQuality,
} from "../services/streamingService";

interface TakePhotoProps {}

const TakePhoto: React.FC<TakePhotoProps> = () => {
  const navigate = useNavigate();

  // Real-time streaming state
  const [isConnected, setIsConnected] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [currentFrame, setCurrentFrame] = useState<string>("");
  const [cleanFrame, setCleanFrame] = useState<string>("");
  const [confidence, setConfidence] = useState(0);
  const [detectionQuality, setDetectionQuality] =
    useState<DetectionQuality | null>(null);
  const [frameCount, setFrameCount] = useState(0);
  const [isAutoStopping, setIsAutoStopping] = useState(false);
  const [bestFrame, setBestFrame] = useState<string>("");
  const [detectionComplete, setDetectionComplete] = useState(false);

  // Confidence tracking for auto-stop
  const [confidenceHistory, setConfidenceHistory] = useState<number[]>([]);
  const [sustainedHighConfidence, setSustainedHighConfidence] = useState(false);
  const [highConfidenceStartTime, setHighConfidenceStartTime] = useState<
    number | null
  >(null);

  const videoRef = useRef<HTMLVideoElement>(null);
  const streamingServiceRef = useRef<StreamingService | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const autoStopTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const confidenceThreshold = 0.75; // High confidence threshold for TakePhoto
  const requiredSustainedTime = 3000; // 3 seconds of sustained confidence

  useEffect(() => {
    initializeStreamingService();
    return () => {
      cleanup();
    };
  }, []);

  // Confidence tracking with auto-stop
  useEffect(() => {
    setConfidenceHistory((prev) => {
      const newHistory = [...prev, confidence];
      return newHistory.slice(-60); // Keep last 60 frames (4 seconds at 15fps)
    });

    if (
      confidence >= confidenceThreshold &&
      !isAutoStopping &&
      isStreaming &&
      !detectionComplete
    ) {
      const now = Date.now();

      if (!highConfidenceStartTime) {
        setHighConfidenceStartTime(now);
        console.log(
          `🎯 High confidence started: ${confidence.toFixed(
            3
          )} >= ${confidenceThreshold}`
        );
      } else {
        const duration = now - highConfidenceStartTime;
        if (duration >= requiredSustainedTime && !sustainedHighConfidence) {
          console.log(
            `✅ Sustained high confidence for ${duration}ms, auto-stopping`
          );
          setSustainedHighConfidence(true);
          setIsAutoStopping(true);

          autoStopTimeoutRef.current = setTimeout(() => {
            stopStreamingAndCapture();
          }, 1000);
        }
      }
    } else {
      if (highConfidenceStartTime && !sustainedHighConfidence) {
        console.log(
          `📉 Confidence dropped: ${confidence.toFixed(
            3
          )} < ${confidenceThreshold}`
        );
        setHighConfidenceStartTime(null);
      }
    }
  }, [
    confidence,
    confidenceThreshold,
    isAutoStopping,
    isStreaming,
    highConfidenceStartTime,
    sustainedHighConfidence,
    detectionComplete,
  ]);

  const initializeStreamingService = async () => {
    try {
      const service = new StreamingService();

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
        setIsAutoStopping(false);
        setDetectionComplete(false);
      });

      service.setOnStreamStopped(() => {
        console.log("⏹️ Stream stopped");
        setIsStreaming(false);
        setIsAutoStopping(false);
      });

      service.setOnAnnotatedFrame((data: AnnotatedFrameData) => {
        setCurrentFrame(data.annotated_frame);
        setCleanFrame(data.clean_frame);
        setConfidence(data.confidence);
        setDetectionQuality(data.detection_quality);
        setFrameCount(data.frame_number);

        // Update best frame if this is better
        if (data.confidence > confidence) {
          setBestFrame(data.clean_frame || data.annotated_frame);
        }
      });

      service.setOnError((errorMsg: string) => {
        console.error("Streaming error:", errorMsg);
        toast.error(errorMsg);
      });

      await service.connect();
      streamingServiceRef.current = service;
    } catch (err) {
      console.error("Failed to initialize streaming service:", err);
      toast.error("Failed to connect to streaming service");
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
        videoConstraints.deviceId = { exact: videoDevices[0].deviceId };
        console.log(
          "Using second camera:",
          videoDevices[0].label || "Camera 2"
        );
        toast.success(`Using camera: ${videoDevices[0].label || "Camera 2"}`);
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

      const stream = await navigator.mediaDevices.getUserMedia({
        video: videoConstraints,
        audio: false,
      });

      streamRef.current = stream;

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play();
        streamingServiceRef.current.setVideoElement(videoRef.current);
      }

      streamingServiceRef.current.startStream({
        detection_mode: "realtime",
        confidence_threshold: confidenceThreshold,
        frame_rate: 15,
      });

      setTimeout(() => {
        streamingServiceRef.current?.startFrameCapture();
      }, 1000);
    } catch (err) {
      console.error("Failed to start streaming:", err);
      toast.error("Failed to start camera stream");
    }
  };

  const stopStreamingAndCapture = () => {
    try {
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

      // Use the best frame captured
      const finalFrame = bestFrame || cleanFrame || currentFrame;
      if (finalFrame) {
        setBestFrame(finalFrame);
        setDetectionComplete(true);
        toast.success("Perfect pose captured! Ready for style analysis.");
      }
    } catch (err) {
      console.error("Failed to stop streaming:", err);
      toast.error("Failed to capture frame");
    }
  };

  const cleanup = () => {
    if (autoStopTimeoutRef.current) {
      clearTimeout(autoStopTimeoutRef.current);
    }
    stopStreamingAndCapture();
    streamingServiceRef.current?.disconnect();
  };

  const proceedToNextStep = () => {
    // Pass the captured frame data to the next page
    const frameToPass = bestFrame || cleanFrame || currentFrame;

    if (!frameToPass) {
      toast.error("No photo captured. Please try the detection again.");
      return;
    }

    console.log("🖼️ Passing captured frame to next step");

    // Navigate to clothing recommendations with the captured user photo
    navigate("/pick_clothes", {
      state: {
        userPhoto: frameToPass,
        detectionData: {
          confidence: confidence,
          frameCount: frameCount,
          detectionQuality: detectionQuality,
        },
      },
    });
  };

  return (
    <div className="min-h-screen bg-gradient-background relative overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute inset-0 opacity-20 pointer-events-none">
        <div className="absolute top-20 left-10 w-72 h-72 bg-primary-glow/30 rounded-full blur-3xl animate-float"></div>
        <div
          className="absolute bottom-20 right-10 w-96 h-96 bg-primary/20 rounded-full blur-3xl animate-float"
          style={{ animationDelay: "1.5s" }}
        ></div>
      </div>

      <div className="relative z-10 container mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8 animate-fade-in">
          <Button
            variant="glass"
            onClick={() => navigate("/")}
            className="flex items-center gap-2"
          >
            <Home className="w-4 h-4" />
            Back to Home
          </Button>

          <div className="flex items-center gap-2 text-white">
            <Sparkles className="w-5 h-5 text-primary-glow" />
            <h1 className="text-xl font-semibold">Style TakePhoto</h1>
          </div>

          <div
            className={`px-4 py-2 rounded-full text-white font-medium ${
              isConnected ? "bg-green-500/80" : "bg-red-500/80"
            } backdrop-blur-sm`}
          >
            {isConnected ? "🟢 Connected" : "🔴 Disconnected"}
          </div>
        </div>

        {/* Main Content */}
        <div className="max-w-4xl mx-auto">
          {/* TakePhoto Steps */}
          {!detectionComplete ? (
            <Card className="bg-white/10 backdrop-blur-md border-white/20 text-white mb-8">
              <CardHeader>
                <CardTitle className="text-center text-3xl font-bold text-white mb-2">
                  Let's Get Started with Your Style Profile
                </CardTitle>
                <p className="text-center text-white/80 text-lg">
                  We'll use AI-powered body detection to understand your unique
                  style preferences
                </p>
              </CardHeader>
              <CardContent className="p-8">
                <div className="grid lg:grid-cols-2 gap-8">
                  {/* Camera Feed */}
                  <div className="text-center">
                    <h3 className="text-xl font-semibold text-white mb-4">
                      Position Yourself for Detection
                    </h3>

                    <div className="relative bg-black rounded-2xl overflow-hidden mb-4">
                      {/* Hidden video element for frame capture */}
                      <video
                        ref={videoRef}
                        autoPlay
                        muted
                        playsInline
                        className="hidden"
                      />

                      {/* Display annotated frame or video preview */}
                      {currentFrame ? (
                        <img
                          src={currentFrame}
                          alt="Real-time body detection"
                          className="w-full h-80 object-contain"
                        />
                      ) : (
                        <div className="w-full h-80 flex items-center justify-center bg-black">
                          <div className="text-white text-center">
                            <Camera className="w-16 h-16 mx-auto mb-4 opacity-50" />
                            <p className="text-lg mb-2">Camera Feed</p>
                            <p className="text-sm opacity-75">
                              Position yourself in the center
                            </p>
                          </div>
                        </div>
                      )}

                      {/* Overlay indicators */}
                      {isStreaming && (
                        <div className="absolute top-4 left-4 bg-black/50 text-white px-3 py-1 rounded-full text-sm">
                          Frame: {frameCount} | Confidence:{" "}
                          {(confidence * 100).toFixed(0)}%
                        </div>
                      )}

                      {isAutoStopping && (
                        <div className="absolute top-4 left-1/2 transform -translate-x-1/2 bg-primary/80 text-white px-4 py-2 rounded-full text-sm font-medium backdrop-blur-sm">
                          ✨ Perfect pose detected! Capturing...
                        </div>
                      )}
                    </div>

                    {/* Control Buttons */}
                    <div className="space-y-4">
                      {!isStreaming ? (
                        <Button
                          variant="hero"
                          size="lg"
                          onClick={startStreaming}
                          disabled={!isConnected}
                          className="w-full"
                        >
                          <Camera className="w-5 h-5 mr-2" />
                          Start Body Detection
                        </Button>
                      ) : !isAutoStopping ? (
                        <Button
                          variant="secondary"
                          size="lg"
                          onClick={stopStreamingAndCapture}
                          className="w-full"
                        >
                          Stop & Use Current Pose
                        </Button>
                      ) : null}
                    </div>
                  </div>

                  {/* Detection Stats */}
                  <div className="space-y-6">
                    <h3 className="text-xl font-semibold text-white mb-4">
                      Detection Progress
                    </h3>

                    {/* Confidence Progress */}
                    <div className="bg-white/10 rounded-xl p-6 backdrop-blur-sm">
                      <div className="flex items-center justify-between mb-3">
                        <span className="text-white font-medium">
                          Detection Confidence
                        </span>
                        <span className="text-primary-glow font-bold">
                          {(confidence * 100).toFixed(1)}%
                        </span>
                      </div>
                      <div className="w-full bg-black/30 rounded-full h-3">
                        <div
                          className="bg-gradient-to-r from-primary to-primary-glow h-3 rounded-full transition-all duration-300"
                          style={{ width: `${confidence * 100}%` }}
                        />
                      </div>
                      <p className="text-white/70 text-sm mt-2">
                        {confidence >= confidenceThreshold
                          ? "Great pose! Hold steady..."
                          : "Position yourself clearly in frame"}
                      </p>
                    </div>

                    {/* Detection Quality Stats */}
                    {detectionQuality && (
                      <div className="grid grid-cols-2 gap-4">
                        <div className="bg-white/10 rounded-lg p-4 text-center backdrop-blur-sm">
                          <div className="text-2xl font-bold text-primary-glow">
                            {detectionQuality.face_count}
                          </div>
                          <div className="text-sm text-white/70">Faces</div>
                        </div>
                        <div className="bg-white/10 rounded-lg p-4 text-center backdrop-blur-sm">
                          <div className="text-2xl font-bold text-primary-glow">
                            {detectionQuality.body_count}
                          </div>
                          <div className="text-sm text-white/70">Bodies</div>
                        </div>
                        <div className="bg-white/10 rounded-lg p-4 text-center backdrop-blur-sm">
                          <div className="text-2xl font-bold text-primary-glow">
                            {detectionQuality.landmark_count}
                          </div>
                          <div className="text-sm text-white/70">Landmarks</div>
                        </div>
                        <div className="bg-white/10 rounded-lg p-4 text-center backdrop-blur-sm">
                          <div className="text-2xl font-bold text-primary-glow">
                            {detectionQuality.brightness.toFixed(0)}
                          </div>
                          <div className="text-sm text-white/70">
                            Brightness
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Instructions */}
                    <div className="bg-white/10 rounded-xl p-6 backdrop-blur-sm">
                      <h4 className="font-semibold text-white mb-3">
                        Tips for Best Results
                      </h4>
                      <ul className="space-y-2 text-sm text-white/80">
                        <li className="flex items-center gap-2">
                          <CheckCircle className="w-4 h-4 text-green-400" />
                          Stand facing the camera directly
                        </li>
                        <li className="flex items-center gap-2">
                          <CheckCircle className="w-4 h-4 text-green-400" />
                          Ensure good lighting on your face and body
                        </li>
                        <li className="flex items-center gap-2">
                          <CheckCircle className="w-4 h-4 text-green-400" />
                          Keep your arms at your sides
                        </li>
                        <li className="flex items-center gap-2">
                          <CheckCircle className="w-4 h-4 text-green-400" />
                          Stay still for accurate detection
                        </li>
                      </ul>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ) : (
            /* Detection Complete */
            <Card className="bg-white/10 backdrop-blur-md border-white/20 text-white">
              <CardHeader>
                <CardTitle className="text-center text-3xl font-bold text-white mb-2">
                  Perfect! Detection Complete
                </CardTitle>
                <p className="text-center text-white/80 text-lg">
                  We've captured your body profile successfully
                </p>
              </CardHeader>
              <CardContent className="p-8">
                <div className="grid lg:grid-cols-2 gap-8 items-center">
                  <div className="text-center">
                    <h3 className="text-xl font-semibold text-white mb-4">
                      Your Captured Profile
                    </h3>
                    {bestFrame && (
                      <img
                        src={bestFrame}
                        alt="Your body profile"
                        className="w-full max-w-md h-80 object-cover rounded-2xl mx-auto border-2 border-primary-glow/30"
                      />
                    )}
                  </div>

                  <div className="space-y-6">
                    <div className="bg-white/10 rounded-xl p-6 backdrop-blur-sm">
                      <div className="flex items-center gap-3 mb-4">
                        <CheckCircle className="w-6 h-6 text-green-400" />
                        <h4 className="font-semibold text-white text-lg">
                          Detection Summary
                        </h4>
                      </div>
                      <div className="space-y-3 text-white/80">
                        <div className="flex justify-between">
                          <span>Final Confidence:</span>
                          <span className="font-medium text-primary-glow">
                            {(confidence * 100).toFixed(1)}%
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span>Frames Processed:</span>
                          <span className="font-medium">{frameCount}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Quality Score:</span>
                          <span className="font-medium text-green-400">
                            Excellent
                          </span>
                        </div>
                      </div>
                    </div>

                    <Button
                      variant="hero"
                      size="lg"
                      onClick={proceedToNextStep}
                      className="w-full"
                    >
                      Continue to Style Recommendations
                      <Sparkles className="w-5 h-5 ml-2" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};

export default TakePhoto;
