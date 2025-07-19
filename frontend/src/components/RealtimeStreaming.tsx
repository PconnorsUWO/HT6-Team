import React, { useState, useRef, useEffect } from "react";
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
}

const RealtimeStreaming: React.FC<RealtimeStreamingProps> = ({
  onFrameSelected,
  onError,
}) => {
  const [isConnected, setIsConnected] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [currentFrame, setCurrentFrame] = useState<string>("");
  const [confidence, setConfidence] = useState(0);
  const [detectionQuality, setDetectionQuality] =
    useState<DetectionQuality | null>(null);
  const [error, setError] = useState<string>("");
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

      // Set up event handlers
      service.setOnConnected(() => {
        console.log("✅ Connected to streaming service");
        setIsConnected(true);
        setError("");
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
        setConfidence(data.confidence);
        setDetectionQuality(data.detection_quality);
        setFrameCount(data.frame_number);
      });

      service.setOnError((errorMsg: string) => {
        console.error("Streaming error:", errorMsg);
        setError(errorMsg);
        onError?.(errorMsg);
      });

      // Connect to backend
      await service.connect();
      streamingServiceRef.current = service;
    } catch (err) {
      console.error("Failed to initialize streaming service:", err);
      setError("Failed to connect to streaming service");
      onError?.("Failed to connect to streaming service");
    }
  };

  const startStreaming = async () => {
    try {
      if (!streamingServiceRef.current) {
        throw new Error("Streaming service not initialized");
      }

      // Get camera access
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 640 },
          height: { ideal: 480 },
          facingMode: "user",
        },
        audio: false,
      });

      streamRef.current = stream;

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play();

        // Set video element in streaming service
        streamingServiceRef.current.setVideoElement(videoRef.current);
      }

      // Start streaming
      streamingServiceRef.current.startStream({
        detection_mode: "realtime",
        confidence_threshold: 0.7,
        frame_rate: 15,
      });

      // Start frame capture after a short delay to ensure video is ready
      setTimeout(() => {
        streamingServiceRef.current?.startFrameCapture();
      }, 1000);
    } catch (err) {
      console.error("Failed to start streaming:", err);
      setError("Failed to start camera stream");
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
    }
  };

  const selectCurrentFrame = () => {
    if (currentFrame && detectionQuality) {
      onFrameSelected?.(currentFrame, {
        annotated_frame: currentFrame,
        confidence,
        frame_number: frameCount,
        timestamp: frameCount / 30.0,
        detection_quality: detectionQuality,
        faces: [],
        bodies: [],
        eyes: [],
        pose_landmarks: [],
      });
    }
  };

  const cleanup = () => {
    stopStreaming();
    streamingServiceRef.current?.disconnect();
  };

  return (
    <div className="bg-white rounded-2xl p-8 shadow-2xl mb-8">
      <h2 className="text-3xl font-bold text-gray-800 text-center mb-4">
        Real-Time Body Detection
      </h2>
      <p className="text-gray-600 text-center mb-8">
        Live camera feed with OpenCV body detection and pose estimation
      </p>

      {/* Connection Status */}
      <div className="flex justify-center mb-6">
        <div
          className={`px-4 py-2 rounded-full text-white font-medium ${
            isConnected ? "bg-green-500" : "bg-red-500"
          }`}
        >
          {isConnected ? "🟢 Connected" : "🔴 Disconnected"}
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
          <strong>Error:</strong> {error}
          <button
            onClick={() => setError("")}
            className="float-right font-bold"
          >
            ×
          </button>
        </div>
      )}

      {/* Video Display */}
      <div className="grid lg:grid-cols-2 gap-8 mb-8">
        {/* Live Camera Feed */}
        <div className="text-center">
          <h3 className="text-xl font-semibold text-gray-700 mb-4">
            Live Camera Feed
          </h3>
          <video
            ref={videoRef}
            autoPlay
            muted
            playsInline
            className="w-full max-w-md h-80 bg-black rounded-2xl mx-auto mb-4"
          />
          <div className="space-x-4">
            {!isStreaming ? (
              <button
                className="bg-green-500 hover:bg-green-600 disabled:bg-gray-400 text-white font-semibold py-3 px-6 rounded-full transition-all duration-300 transform hover:scale-105 disabled:cursor-not-allowed"
                onClick={startStreaming}
                disabled={!isConnected}
              >
                🎥 Start Detection
              </button>
            ) : (
              <button
                className="bg-red-500 hover:bg-red-600 text-white font-semibold py-3 px-6 rounded-full transition-all duration-300 transform hover:scale-105"
                onClick={stopStreaming}
              >
                ⏹️ Stop Detection
              </button>
            )}
          </div>
        </div>

        {/* Annotated Frame */}
        <div className="text-center">
          <h3 className="text-xl font-semibold text-gray-700 mb-4">
            Detected Body Parts
          </h3>
          {currentFrame ? (
            <div className="relative">
              <img
                src={currentFrame}
                alt="Annotated frame with body detection"
                className="w-full max-w-md h-80 object-cover rounded-2xl mx-auto mb-4 border-2 border-gray-200"
              />
              <button
                className="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 px-4 rounded-full transition-all duration-300 transform hover:scale-105"
                onClick={selectCurrentFrame}
              >
                📸 Select This Frame
              </button>
            </div>
          ) : (
            <div className="w-full max-w-md h-80 bg-gray-100 rounded-2xl mx-auto mb-4 flex items-center justify-center">
              <p className="text-gray-500">No detection data yet</p>
            </div>
          )}
        </div>
      </div>

      {/* Detection Stats */}
      {detectionQuality && (
        <div className="bg-gray-50 rounded-xl p-6">
          <h3 className="text-xl font-semibold text-gray-700 mb-4 text-center">
            Detection Statistics
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-white rounded-lg p-4 text-center border-l-4 border-green-500">
              <div className="text-2xl font-bold text-green-600">
                {(confidence * 100).toFixed(1)}%
              </div>
              <div className="text-sm text-gray-600">Confidence</div>
            </div>
            <div className="bg-white rounded-lg p-4 text-center border-l-4 border-blue-500">
              <div className="text-2xl font-bold text-blue-600">
                {detectionQuality.face_count}
              </div>
              <div className="text-sm text-gray-600">Faces</div>
            </div>
            <div className="bg-white rounded-lg p-4 text-center border-l-4 border-purple-500">
              <div className="text-2xl font-bold text-purple-600">
                {detectionQuality.body_count}
              </div>
              <div className="text-sm text-gray-600">Bodies</div>
            </div>
            <div className="bg-white rounded-lg p-4 text-center border-l-4 border-orange-500">
              <div className="text-2xl font-bold text-orange-600">
                {detectionQuality.landmark_count}
              </div>
              <div className="text-sm text-gray-600">Landmarks</div>
            </div>
          </div>

          <div className="mt-4 grid grid-cols-2 gap-4">
            <div className="bg-white rounded-lg p-4 border-l-4 border-yellow-500">
              <div className="text-lg font-semibold text-gray-800">
                Brightness: {detectionQuality.brightness.toFixed(0)}
              </div>
              <div className="text-sm text-gray-600">Image Quality</div>
            </div>
            <div className="bg-white rounded-lg p-4 border-l-4 border-indigo-500">
              <div className="text-lg font-semibold text-gray-800">
                Frame: {frameCount}
              </div>
              <div className="text-sm text-gray-600">Processed</div>
            </div>
          </div>
        </div>
      )}

      {/* Legend */}
      <div className="mt-6 bg-white rounded-lg p-4 border border-gray-200">
        <h4 className="font-semibold text-gray-800 mb-3">Detection Legend</h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div className="flex items-center">
            <div className="w-4 h-4 bg-green-500 rounded mr-2"></div>
            <span>Green: Face Detection</span>
          </div>
          <div className="flex items-center">
            <div className="w-4 h-4 bg-blue-500 rounded mr-2"></div>
            <span>Blue: Body Detection</span>
          </div>
          <div className="flex items-center">
            <div className="w-4 h-4 bg-yellow-500 rounded mr-2"></div>
            <span>Yellow: Eye Detection</span>
          </div>
          <div className="flex items-center">
            <div className="w-4 h-4 bg-purple-500 rounded mr-2"></div>
            <span>Purple: Pose Landmarks</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RealtimeStreaming;
