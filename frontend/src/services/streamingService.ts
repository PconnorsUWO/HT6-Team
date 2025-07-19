import io from "socket.io-client";

export interface DetectionQuality {
  brightness: number;
  contrast: number;
  face_count: number;
  body_count: number;
  landmark_count: number;
  total_confidence: number;
}

export interface BodyPart {
  x: number;
  y: number;
  width: number;
  height: number;
  confidence: number;
}

export interface PoseLandmark {
  id: number;
  x: number;
  y: number;
  confidence: number;
  name: string;
}

export interface AnnotatedFrameData {
  annotated_frame: string;
  confidence: number;
  frame_number: number;
  timestamp: number;
  detection_quality: DetectionQuality;
  faces: BodyPart[];
  bodies: BodyPart[];
  eyes: BodyPart[];
  pose_landmarks: PoseLandmark[];
}

export interface StreamConfig {
  detection_mode?: "realtime" | "strict" | "performance";
  confidence_threshold?: number;
  frame_rate?: number;
}

interface StreamStartedData {
  status: string;
  message: string;
  detection_mode: string;
  confidence_threshold: number;
}

interface StreamStoppedData {
  status: string;
  message: string;
}

interface ErrorData {
  error: string;
}

class StreamingService {
  private socket: ReturnType<typeof io> | null = null;
  private isConnected = false;
  private isStreaming = false;
  private frameRate = 15; // FPS
  private frameInterval: number | null = null;
  private videoElement: HTMLVideoElement | null = null;
  private canvas: HTMLCanvasElement | null = null;
  private ctx: CanvasRenderingContext2D | null = null;

  // Event callbacks
  private onConnected?: () => void;
  private onDisconnected?: () => void;
  private onAnnotatedFrame?: (data: AnnotatedFrameData) => void;
  private onStreamStarted?: () => void;
  private onStreamStopped?: () => void;
  private onError?: (error: string) => void;

  constructor() {
    this.setupCanvas();
  }

  private setupCanvas(): void {
    this.canvas = document.createElement("canvas");
    this.ctx = this.canvas.getContext("2d");
  }

  connect(url: string = "http://127.0.0.1:5000"): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.socket = io(url, {
          transports: ["websocket", "polling"],
          timeout: 10000,
        });

        this.socket.on("connect", () => {
          console.log("✅ Connected to streaming service");
          this.isConnected = true;
          this.onConnected?.();
          resolve();
        });

        this.socket.on("disconnect", () => {
          console.log("❌ Disconnected from streaming service");
          this.isConnected = false;
          this.onDisconnected?.();
        });

        this.socket.on("connected", (data: Record<string, unknown>) => {
          console.log("Streaming service ready:", data);
        });

        this.socket.on("stream_started", (data: StreamStartedData) => {
          console.log("Stream started:", data);
          this.isStreaming = true;
          this.onStreamStarted?.();
        });

        this.socket.on("stream_stopped", (data: StreamStoppedData) => {
          console.log("Stream stopped:", data);
          this.isStreaming = false;
          this.onStreamStopped?.();
        });

        this.socket.on("annotated_frame", (data: AnnotatedFrameData) => {
          console.log("📡 Received annotated frame from backend:", {
            hasFrame: !!data.annotated_frame,
            confidence: data.confidence,
            frameNumber: data.frame_number,
          });
          this.onAnnotatedFrame?.(data);
        });

        this.socket.on("frame_error", (data: ErrorData) => {
          console.error("Frame processing error:", data);
          this.onError?.(data.error || "Frame processing error");
        });

        this.socket.on("stream_error", (data: ErrorData) => {
          console.error("Stream error:", data);
          this.onError?.(data.error || "Stream error");
        });

        this.socket.on("connect_error", (error: Error) => {
          console.error("Connection error:", error);
          reject(error);
        });
      } catch (error) {
        console.error("Failed to connect:", error);
        reject(error);
      }
    });
  }

  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
    this.isConnected = false;
    this.isStreaming = false;
    this.stopFrameCapture();
  }

  startStream(config: StreamConfig = {}): void {
    if (!this.socket || !this.isConnected) {
      throw new Error("Not connected to streaming service");
    }

    const streamConfig = {
      detection_mode: config.detection_mode || "realtime",
      confidence_threshold: config.confidence_threshold || 0.7,
      frame_rate: config.frame_rate || this.frameRate,
    };

    this.frameRate = streamConfig.frame_rate;
    this.socket.emit("start_stream", streamConfig);
  }

  stopStream(): void {
    if (this.socket && this.isConnected) {
      this.socket.emit("stop_stream");
    }
    this.stopFrameCapture();
  }

  setVideoElement(video: HTMLVideoElement): void {
    console.log("🎥 Setting video element in streaming service", {
      hasVideo: !!video,
      videoWidth: video?.videoWidth,
      videoHeight: video?.videoHeight,
    });
    this.videoElement = video;
  }

  startFrameCapture(): void {
    if (!this.videoElement || !this.canvas || !this.ctx || !this.socket) {
      console.error("❌ Cannot start frame capture: missing components");
      return;
    }

    this.stopFrameCapture(); // Stop any existing capture

    const captureFrame = () => {
      if (
        !this.videoElement ||
        !this.canvas ||
        !this.ctx ||
        !this.socket ||
        !this.isStreaming
      ) {
        return;
      }

      try {
        // Simple check for video readiness
        if (
          this.videoElement.videoWidth === 0 ||
          this.videoElement.videoHeight === 0
        ) {
          return;
        }

        // Set canvas size to match video
        this.canvas.width = this.videoElement.videoWidth;
        this.canvas.height = this.videoElement.videoHeight;

        // Draw video frame to canvas
        this.ctx.drawImage(this.videoElement, 0, 0);

        // Convert to base64
        const frameData = this.canvas.toDataURL("image/jpeg", 0.8);

        // Send frame to backend
        this.socket.emit("video_frame", { frame: frameData });
      } catch (error) {
        console.error("Error capturing frame:", error);
      }
    };

    // Start frame capture at specified frame rate
    this.frameInterval = window.setInterval(
      captureFrame,
      1000 / this.frameRate
    );
    console.log("✅ Frame capture started");
  }

  stopFrameCapture(): void {
    if (this.frameInterval) {
      clearInterval(this.frameInterval);
      this.frameInterval = null;
    }
  }

  // Event setters
  setOnConnected(callback: () => void): void {
    this.onConnected = callback;
  }

  setOnDisconnected(callback: () => void): void {
    this.onDisconnected = callback;
  }

  setOnAnnotatedFrame(callback: (data: AnnotatedFrameData) => void): void {
    this.onAnnotatedFrame = callback;
  }

  setOnStreamStarted(callback: () => void): void {
    this.onStreamStarted = callback;
  }

  setOnStreamStopped(callback: () => void): void {
    this.onStreamStopped = callback;
  }

  setOnError(callback: (error: string) => void): void {
    this.onError = callback;
  }

  // Getters
  getIsConnected(): boolean {
    return this.isConnected;
  }

  getIsStreaming(): boolean {
    return this.isStreaming;
  }

  getFrameRate(): number {
    return this.frameRate;
  }

  isReadyForFrameCapture(): boolean {
    return !!(
      this.videoElement &&
      this.canvas &&
      this.ctx &&
      this.socket &&
      this.isStreaming &&
      this.videoElement.videoWidth > 0 &&
      this.videoElement.videoHeight > 0 &&
      this.videoElement.readyState >= 2
    );
  }
}

export default StreamingService;
