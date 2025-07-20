import React, { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Camera,
  Sparkles,
  CheckCircle,
  AlertCircle,
  Activity,
} from "lucide-react";
import { toast } from "sonner";
import StreamingService from "../services/streamingService";
import type {
  AnnotatedFrameData,
  DetectionQuality,
} from "../services/streamingService";

interface RealtimeStreamingProps {
  onFrameSelected?: (
    frameData: string,
    detectionData: AnnotatedFrameData
  ) => void;
  onError?: (error: string) => void;
  confidenceThreshold?: number;
}

const RealtimeStreaming: React.FC<RealtimeStreamingProps> = ({
  onFrameSelected,
  onError,
  confidenceThreshold = 0.7,
}) => {
  const [isConnected, setIsConnected] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [currentFrame, setCurrentFrame] = useState<string>("");
  const [cleanFrame, setCleanFrame] = useState<string>("");
  const [confidence, setConfidence] = useState(0);
  const [detectionQuality, setDetectionQuality] =
    useState<DetectionQuality | null>(null);
  const [frameCount, setFrameCount] = useState(0);

  const videoRef = useRef<HTMLVideoElement>(null);
  const streamingServiceRef = useRef<StreamingService | null>(null);
  const streamRef = useRef<MediaStream | null>(null);

  useEffect(() => {
    initializeStreamingService();
    return () => {
      cleanup();
    };
  }, []);

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
      });

      service.setOnStreamStopped(() => {
        console.log("⏹️ Stream stopped");
        setIsStreaming(false);
      });

      service.setOnAnnotatedFrame((data: AnnotatedFrameData) => {
        setCurrentFrame(data.annotated_frame);
        setCleanFrame(data.clean_frame);
        setConfidence(data.confidence);
        setDetectionQuality(data.detection_quality);
        setFrameCount(data.frame_number);
      });

      service.setOnError((errorMsg: string) => {
        console.error("Streaming error:", errorMsg);
        toast.error(errorMsg);
        onError?.(errorMsg);
      });

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
      onError?.("Failed to start camera stream");
    }
  };

  const stopStreaming = () => {
    try {
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

  const selectCurrentFrame = () => {
    if (currentFrame && detectionQuality) {
      onFrameSelected?.(cleanFrame || currentFrame, {
        annotated_frame: currentFrame,
        clean_frame: cleanFrame || currentFrame,
        confidence,
        frame_number: frameCount,
        timestamp: frameCount / 30.0,
        detection_quality: detectionQuality,
        faces: [],
        bodies: [],
        eyes: [],
        pose_landmarks: [],
      });
      toast.success("Frame selected successfully!");
    }
  };

  const cleanup = () => {
    stopStreaming();
    streamingServiceRef.current?.disconnect();
  };

  return (
    <Card className="bg-white/10 backdrop-blur-md border-white/20 text-white shadow-elegant">
      <CardHeader>
        <CardTitle className="text-center text-3xl font-bold text-white mb-2 flex items-center justify-center gap-3">
          <Sparkles className="w-8 h-8 text-primary-glow" />
          Real-Time Body Detection
        </CardTitle>
        <p className="text-center text-white/80 text-lg">
          Live camera feed with AI-powered body detection and pose estimation
        </p>
      </CardHeader>

      <CardContent className="p-8">
        {/* Connection Status */}
        <div className="flex justify-center mb-6">
          <div
            className={`px-6 py-3 rounded-full text-white font-medium backdrop-blur-sm transition-all duration-300 ${
              isConnected ? "bg-green-500/80 shadow-soft" : "bg-red-500/80"
            }`}
          >
            <div className="flex items-center gap-2">
              <Activity
                className={`w-4 h-4 ${isConnected ? "animate-pulse" : ""}`}
              />
              {isConnected ? "🟢 Connected" : "🔴 Disconnected"}
            </div>
          </div>
        </div>

        {/* Video Display */}
        <div className="grid lg:grid-cols-2 gap-8 mb-8">
          {/* Live Camera Feed */}
          <div className="text-center space-y-4">
            <h3 className="text-xl font-semibold text-white mb-4 flex items-center justify-center gap-2">
              <Camera className="w-5 h-5 text-primary-glow" />
              Live Camera Feed
            </h3>

            <div className="relative bg-black rounded-2xl overflow-hidden shadow-elegant">
              <video
                ref={videoRef}
                autoPlay
                muted
                playsInline
                className="w-full h-80 object-cover"
              />

              {!isStreaming && (
                <div className="absolute inset-0 flex items-center justify-center bg-black/50 backdrop-blur-sm">
                  <div className="text-white text-center">
                    <Camera className="w-16 h-16 mx-auto mb-4 opacity-50" />
                    <p className="text-lg">Camera Ready</p>
                    <p className="text-sm opacity-75">
                      Click start to begin detection
                    </p>
                  </div>
                </div>
              )}
            </div>

            <div className="space-y-3">
              {!isStreaming ? (
                <Button
                  variant="hero"
                  size="lg"
                  onClick={startStreaming}
                  disabled={!isConnected}
                  className="w-full"
                >
                  <Camera className="w-5 h-5 mr-2" />
                  Start Detection
                </Button>
              ) : (
                <Button
                  variant="secondary"
                  size="lg"
                  onClick={stopStreaming}
                  className="w-full"
                >
                  Stop Detection
                </Button>
              )}
            </div>
          </div>

          {/* Annotated Frame */}
          <div className="text-center space-y-4">
            <h3 className="text-xl font-semibold text-white mb-4 flex items-center justify-center gap-2">
              <Sparkles className="w-5 h-5 text-primary-glow" />
              Detected Body Parts
            </h3>

            {currentFrame ? (
              <div className="relative space-y-4">
                <div className="relative bg-black rounded-2xl overflow-hidden shadow-elegant">
                  <img
                    src={currentFrame}
                    alt="Annotated frame with body detection"
                    className="w-full h-80 object-cover"
                  />

                  <div className="absolute top-4 left-4 bg-black/50 text-white px-3 py-1 rounded-full text-sm backdrop-blur-sm">
                    Frame: {frameCount} | Confidence:{" "}
                    {(confidence * 100).toFixed(0)}%
                  </div>
                </div>

                <Button
                  variant="hero"
                  size="lg"
                  onClick={selectCurrentFrame}
                  className="w-full"
                >
                  <CheckCircle className="w-5 h-5 mr-2" />
                  Select This Frame
                </Button>
              </div>
            ) : (
              <div className="w-full h-80 bg-black/30 rounded-2xl flex items-center justify-center backdrop-blur-sm border border-white/10">
                <div className="text-white/60 text-center">
                  <Sparkles className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p className="text-lg">No detection data yet</p>
                  <p className="text-sm">Start streaming to see results</p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Detection Stats */}
        {detectionQuality && (
          <Card className="bg-white/10 backdrop-blur-sm border-white/20">
            <CardContent className="p-6">
              <h3 className="text-xl font-semibold text-white mb-6 text-center flex items-center justify-center gap-2">
                <Activity className="w-5 h-5 text-primary-glow" />
                Detection Statistics
              </h3>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                <div className="bg-white/10 rounded-lg p-4 text-center border border-primary/30 backdrop-blur-sm">
                  <div className="text-2xl font-bold text-primary-glow">
                    {(confidence * 100).toFixed(1)}%
                  </div>
                  <div className="text-sm text-white/70">Confidence</div>
                </div>
                <div className="bg-white/10 rounded-lg p-4 text-center border border-blue-500/30 backdrop-blur-sm">
                  <div className="text-2xl font-bold text-blue-400">
                    {detectionQuality.face_count}
                  </div>
                  <div className="text-sm text-white/70">Faces</div>
                </div>
                <div className="bg-white/10 rounded-lg p-4 text-center border border-purple-500/30 backdrop-blur-sm">
                  <div className="text-2xl font-bold text-purple-400">
                    {detectionQuality.body_count}
                  </div>
                  <div className="text-sm text-white/70">Bodies</div>
                </div>
                <div className="bg-white/10 rounded-lg p-4 text-center border border-orange-500/30 backdrop-blur-sm">
                  <div className="text-2xl font-bold text-orange-400">
                    {detectionQuality.landmark_count}
                  </div>
                  <div className="text-sm text-white/70">Landmarks</div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="bg-white/10 rounded-lg p-4 border border-yellow-500/30 backdrop-blur-sm">
                  <div className="text-lg font-semibold text-white">
                    Brightness: {detectionQuality.brightness.toFixed(0)}
                  </div>
                  <div className="text-sm text-white/70">Image Quality</div>
                </div>
                <div className="bg-white/10 rounded-lg p-4 border border-indigo-500/30 backdrop-blur-sm">
                  <div className="text-lg font-semibold text-white">
                    Frame: {frameCount}
                  </div>
                  <div className="text-sm text-white/70">Processed</div>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Legend */}
        <Card className="mt-6 bg-white/10 backdrop-blur-sm border-white/20">
          <CardContent className="p-4">
            <h4 className="font-semibold text-white mb-3 flex items-center gap-2">
              <CheckCircle className="w-4 h-4 text-primary-glow" />
              Detection Legend
            </h4>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-green-500 rounded"></div>
                <span className="text-white/80">Face Detection</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-blue-500 rounded"></div>
                <span className="text-white/80">Body Detection</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-yellow-500 rounded"></div>
                <span className="text-white/80">Eye Detection</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-purple-500 rounded"></div>
                <span className="text-white/80">Pose Landmarks</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </CardContent>
    </Card>
  );
};

export default RealtimeStreaming;
