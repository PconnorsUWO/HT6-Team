import { useState, useRef, useEffect } from "react";
import ApiTester from "./ApiTester";
import RealtimeStreaming from "./components/RealtimeStreaming";
import type { AnnotatedFrameData } from "./services/streamingService";

interface Garment {
  id: string;
  name: string;
  description: string;
  image_url: string;
}

interface Recommendation {
  name: string;
  description: string;
  style_category: string;
  color_suggestion?: string;
}

interface TryOnResult {
  result_id: string;
  result_image: string;
  public_url: string;
  recommendations: Recommendation[];
  message: string;
}

interface BodyDetectionResult {
  success: boolean;
  best_frame?: string; // base64 data URL from OpenCV
  confidence?: number;
  frame_number?: number;
  detection_mode?: string;
  annotations?: {
    faces: Array<{
      x: number;
      y: number;
      width: number;
      height: number;
      area_ratio?: number;
    }>;
    bodies: Array<{
      x: number;
      y: number;
      width: number;
      height: number;
      area_ratio?: number;
    }>;
    detection_quality?: {
      face_confidence: number;
      body_confidence: number;
      quality_score: number;
      brightness_confidence: number;
      contrast_confidence: number;
      total_confidence: number;
      brightness: number;
      contrast: number;
    };
  };
  message: string;
}

function App() {
  const [currentStep, setCurrentStep] = useState(1);
  const [garments, setGarments] = useState<Garment[]>([]);
  const [selectedGarment, setSelectedGarment] = useState<string>("");
  const [customGarment, setCustomGarment] = useState<File | null>(null);
  const [videoBlob, setVideoBlob] = useState<Blob | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [selectedFrame, setSelectedFrame] = useState<string>("");
  const [bodyDetectionResult, setBodyDetectionResult] =
    useState<BodyDetectionResult | null>(null);
  const [tryOnResult, setTryOnResult] = useState<TryOnResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>("");
  const [recordingDuration, setRecordingDuration] = useState(0);

  // New state for real-time streaming
  const [useRealtimeStreaming, setUseRealtimeStreaming] = useState(true);
  const [realtimeDetectionData, setRealtimeDetectionData] =
    useState<AnnotatedFrameData | null>(null);

  const videoRef = useRef<HTMLVideoElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const mimeTypeRef = useRef<string>("");
  const durationIntervalRef = useRef<number | null>(null);

  useEffect(() => {
    console.log("recording duration", recordingDuration);
  }, [recordingDuration]);

  const API_BASE = "http://127.0.0.1:5000";

  // Load preset garments on component mount
  useEffect(() => {
    // First test if backend is accessible
    testBackendConnection();
    fetchPresetGarments();
  }, []);

  const testBackendConnection = async () => {
    try {
      const response = await fetch(`${API_BASE}/test`);
      const data = await response.json();
      console.log("✅ Backend connection test:", data);
    } catch (err) {
      console.error("❌ Backend connection failed:", err);
      setError(
        "Cannot connect to backend server. Please ensure the backend is running on http://127.0.0.1:5000"
      );
    }
  };

  const fetchPresetGarments = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/preset-garments`);
      const data = await response.json();
      if (data.success) {
        setGarments(data.garments);
      }
    } catch (err) {
      console.error("Error fetching garments:", err);
      setError("Failed to load preset garments");
    }
  };

  const uploadCustomGarment = async (file: File) => {
    const formData = new FormData();
    formData.append("garment_image", file);
    formData.append("user_id", "test_user_123");
    formData.append("description", "Custom uploaded garment");

    try {
      const response = await fetch(`${API_BASE}/api/upload-garment`, {
        method: "POST",
        body: formData,
      });
      const data = await response.json();
      if (data.success) {
        setSelectedGarment(data.garment_id);
        setError("");
      } else {
        setError(data.error || "Failed to upload garment");
      }
    } catch (err) {
      console.error("Error uploading garment:", err);
      setError("Failed to upload garment");
    }
  };

  // New handler for real-time frame selection
  const handleFrameSelected = (
    frameData: string,
    detectionData: AnnotatedFrameData
  ) => {
    setSelectedFrame(frameData);
    setRealtimeDetectionData(detectionData);
    setCurrentStep(4); // Move directly to try-on step
  };

  // New handler for real-time streaming errors
  const handleStreamingError = (errorMsg: string) => {
    setError(errorMsg);
  };

  const startVideoRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: 540,
          height: 960,
          facingMode: "user",
        },
      });

      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }

      // Check for supported video formats in order of preference
      // Browsers typically support WebM better than MP4 for recording
      const supportedFormats = [
        "video/webm;codecs=vp9",
        "video/webm;codecs=vp8",
        "video/webm",
        "video/mp4;codecs=h264",
        "video/mp4",
      ];

      let mimeType = "";
      for (const format of supportedFormats) {
        if (MediaRecorder.isTypeSupported(format)) {
          mimeType = format;
          break;
        }
      }

      if (!mimeType) {
        throw new Error("No supported video format found for recording");
      }

      console.log(`Using video format: ${mimeType}`);

      // Store mimeType in a ref so it can be accessed in other functions
      mimeTypeRef.current = mimeType;

      // Log supported formats for debugging
      console.log("Supported formats check:");
      supportedFormats.forEach((format) => {
        console.log(`${format}: ${MediaRecorder.isTypeSupported(format)}`);
      });

      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: mimeType,
        videoBitsPerSecond: 2500000, // 2.5 Mbps for better quality
      });

      const chunks: Blob[] = [];
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunks.push(event.data);
          console.log(`Received chunk: ${event.data.size} bytes`);
        }
      };

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunks, { type: mimeType });
        console.log(
          `Recording complete: ${blob.size} bytes, type: ${blob.type}`
        );
        setVideoBlob(blob);
        // Stay on step 2 to show the video preview
      };

      mediaRecorderRef.current = mediaRecorder;
      mediaRecorder.start(1000); // Collect data every second for better reliability
      setIsRecording(true);

      const startTime = Date.now();
      setRecordingDuration(0);
      setError("");

      // Start duration timer
      const durationInterval = setInterval(() => {
        const duration = Math.floor((Date.now() - startTime) / 1000);
        setRecordingDuration(duration);
        console.log(`Recording duration: ${duration}s`);
      }, 1000);

      // Store interval ID for cleanup
      durationIntervalRef.current = durationInterval;
    } catch (err) {
      console.error("Error starting video recording:", err);
      setError(
        "Failed to start video recording. Please check camera permissions."
      );
    }
  };

  const stopVideoRecording = () => {
    console.log("stopping video recording");
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      // setRecordingDuration(0);

      // Clear duration interval
      if (durationIntervalRef.current) {
        clearInterval(durationIntervalRef.current);
        durationIntervalRef.current = null;
      }

      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop());
      }
    }
  };

  const processVideo = async () => {
    if (!videoBlob) {
      console.error("No video blob found");
      return;
    }

    // Validate minimum recording duration
    if (recordingDuration < 4) {
      setError(
        "Video must be at least 4 seconds long for processing. Please record a longer video."
      );
      return;
    }

    console.log("Processing video blob:", {
      size: videoBlob.size,
      type: videoBlob.type,
      mimeType: mimeTypeRef.current,
      duration: recordingDuration,
    });

    setLoading(true);
    setError("");
    setCurrentStep(3); // Move to processing step

    try {
      console.log("Uploading video for OpenCV body detection");

      // Step 1: Upload video for OpenCV body detection
      const uploadFormData = new FormData();

      // Determine file extension based on the actual MIME type used
      let fileExtension = "webm"; // default to webm since browsers prefer it
      if (mimeTypeRef.current.includes("mp4")) {
        fileExtension = "mp4";
      } else if (mimeTypeRef.current.includes("webm")) {
        fileExtension = "webm";
      }

      console.log(
        `Using file extension: ${fileExtension} for MIME type: ${mimeTypeRef.current}`
      );

      uploadFormData.append(
        "video_file",
        videoBlob,
        `recording.${fileExtension}`
      );

      // Step 2: Process video with OpenCV body detection
      console.log("Processing video with OpenCV body detection");
      const processResponse = await fetch(`${API_BASE}/api/detect-body`, {
        method: "POST",
        body: uploadFormData,
      });

      const processData: BodyDetectionResult = await processResponse.json();
      if (processData.success && processData.best_frame) {
        setSelectedFrame(processData.best_frame);
        setBodyDetectionResult(processData);
        setCurrentStep(4);
        console.log(
          `Body detection successful with confidence: ${processData.confidence}`
        );
      } else {
        setError(processData.message || "Failed to detect body in video");
      }
    } catch (err) {
      console.error("Error processing video:", err);
      setError("Failed to process video");
    } finally {
      setLoading(false);
    }
  };

  const performTryOn = async () => {
    if (!selectedGarment || !selectedFrame) return;

    setLoading(true);
    setError("");

    try {
      // Convert base64 data URL to a file for upload
      const base64Data = selectedFrame.replace(
        /^data:image\/[a-z]+;base64,/,
        ""
      );
      const byteCharacters = atob(base64Data);
      const byteNumbers = new Array(byteCharacters.length);
      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
      }
      const byteArray = new Uint8Array(byteNumbers);
      const blob = new Blob([byteArray], { type: "image/jpeg" });

      const formData = new FormData();
      formData.append("person_image", blob, "detected_frame.jpg");
      formData.append("garment_id", selectedGarment);
      formData.append("user_id", "test_user_123");

      const response = await fetch(`${API_BASE}/api/tryon`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      if (data.success) {
        setTryOnResult(data);
        setCurrentStep(5);
      } else {
        setError(data.error || "Failed to perform try-on");
      }
    } catch (err) {
      console.error("Error performing try-on:", err);
      setError("Failed to perform try-on");
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setCustomGarment(file);
      uploadCustomGarment(file);
    }
  };

  const resetApp = () => {
    setCurrentStep(1);
    setSelectedGarment("");
    setCustomGarment(null);
    setVideoBlob(null);
    setSelectedFrame("");
    setBodyDetectionResult(null);
    setTryOnResult(null);
    setError("");
    setLoading(false);
    setRealtimeDetectionData(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-500 via-purple-500 to-pink-500 font-sans">
      {/* Header */}
      <header className="text-center py-8 px-4 bg-black/10 backdrop-blur-md">
        <h1 className="text-4xl md:text-5xl font-bold text-white mb-2 drop-shadow-lg">
          🎽 Virtual Try-On App
        </h1>
        <p className="text-lg text-white/90">
          AI-Powered Clothing Try-On with Real-Time OpenCV Body Detection
        </p>
      </header>

      {/* Progress Bar */}
      <div className="flex justify-center items-center py-4 px-4 bg-white/10 backdrop-blur-md mb-8">
        <div className="flex flex-wrap justify-center gap-2">
          {[1, 2, 3, 4, 5].map((step) => (
            <div
              key={step}
              className={`px-6 py-3 rounded-full font-medium transition-all duration-300 ${
                currentStep >= step
                  ? "bg-green-500 text-white shadow-lg scale-105"
                  : "bg-white/20 text-white/70"
              }`}
            >
              {step === 1 && "1. Garment Selection"}
              {step === 2 && "2. Body Detection"}
              {step === 3 && "3. Processing"}
              {step === 4 && "4. Try-On"}
              {step === 5 && "5. Results"}
            </div>
          ))}
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="max-w-2xl mx-auto mb-8 px-4">
          <div className="bg-red-500 text-white p-4 rounded-lg text-center shadow-lg">
            {error}
            <button
              onClick={testBackendConnection}
              className="ml-4 bg-white text-red-500 px-3 py-1 rounded text-sm hover:bg-gray-100"
            >
              Test Connection
            </button>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="max-w-6xl mx-auto px-4">
        {/* Step 1: Garment Selection */}
        {currentStep === 1 && (
          <div className="bg-white rounded-2xl p-8 shadow-2xl mb-8">
            <h2 className="text-3xl font-bold text-gray-800 text-center mb-8">
              Step 1: Select a Garment
            </h2>

            <div className="grid lg:grid-cols-3 gap-8">
              {/* Preset Garments */}
              <div className="lg:col-span-2">
                <h3 className="text-xl font-semibold text-gray-700 mb-4">
                  Preset Garments
                </h3>
                <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
                  {garments.map((garment) => (
                    <div
                      key={garment.id}
                      className={`bg-gray-50 border-2 rounded-xl p-4 text-center cursor-pointer transition-all duration-300 hover:-translate-y-1 hover:shadow-lg ${
                        selectedGarment === garment.id
                          ? "border-green-500 bg-green-50 shadow-lg"
                          : "border-gray-200 hover:border-gray-300"
                      }`}
                      onClick={() => setSelectedGarment(garment.id)}
                    >
                      <img
                        src={garment.image_url}
                        alt={garment.name}
                        className="w-full h-40 object-cover rounded-lg mb-3"
                      />
                      <h4 className="font-semibold text-gray-800 mb-1">
                        {garment.name}
                      </h4>
                      <p className="text-sm text-gray-600">
                        {garment.description}
                      </p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Custom Garment Upload */}
              <div className="bg-gray-50 rounded-xl p-6 text-center">
                <h3 className="text-xl font-semibold text-gray-700 mb-4">
                  Upload Custom Garment
                </h3>
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleFileUpload}
                  className="w-full p-4 border-2 border-dashed border-gray-300 rounded-lg bg-white cursor-pointer transition-colors hover:border-green-500 hover:bg-green-50"
                />
                {customGarment && (
                  <p className="mt-3 text-green-600 font-medium">
                    ✅ {customGarment.name} uploaded successfully!
                  </p>
                )}
              </div>
            </div>

            <div className="text-center mt-8">
              <button
                className="bg-blue-500 hover:bg-blue-600 disabled:bg-gray-400 text-white font-semibold py-3 px-8 rounded-full transition-all duration-300 transform hover:scale-105 disabled:cursor-not-allowed"
                onClick={() => setCurrentStep(2)}
                disabled={!selectedGarment}
              >
                Next: Body Detection
              </button>
            </div>
          </div>
        )}

        {/* Step 2: Body Detection (Real-time or Recording) */}
        {currentStep === 2 && (
          <div className="mb-8">
            {/* Detection Mode Selection */}
            <div className="bg-white rounded-2xl p-6 shadow-2xl mb-6">
              <h3 className="text-xl font-semibold text-gray-700 mb-4 text-center">
                Choose Detection Mode
              </h3>
              <div className="grid md:grid-cols-2 gap-4">
                <button
                  className={`p-6 rounded-xl border-2 transition-all duration-300 ${
                    useRealtimeStreaming
                      ? "border-green-500 bg-green-50 shadow-lg"
                      : "border-gray-200 hover:border-gray-300"
                  }`}
                  onClick={() => setUseRealtimeStreaming(true)}
                >
                  <div className="text-2xl mb-2">🎥</div>
                  <h4 className="font-semibold text-gray-800 mb-2">
                    Real-Time Detection
                  </h4>
                  <p className="text-sm text-gray-600">
                    Live camera feed with instant body detection and pose
                    estimation
                  </p>
                </button>
                <button
                  className={`p-6 rounded-xl border-2 transition-all duration-300 ${
                    !useRealtimeStreaming
                      ? "border-green-500 bg-green-50 shadow-lg"
                      : "border-gray-200 hover:border-gray-300"
                  }`}
                  onClick={() => setUseRealtimeStreaming(false)}
                >
                  <div className="text-2xl mb-2">📹</div>
                  <h4 className="font-semibold text-gray-800 mb-2">
                    Video Recording
                  </h4>
                  <p className="text-sm text-gray-600">
                    Record a video and find the best frame for body detection
                  </p>
                </button>
              </div>
            </div>

            {/* Real-time Streaming Component */}
            {useRealtimeStreaming && (
              <RealtimeStreaming
                onFrameSelected={handleFrameSelected}
                onError={handleStreamingError}
              />
            )}

            {/* Legacy Video Recording */}
            {!useRealtimeStreaming && (
              <div className="bg-white rounded-2xl p-8 shadow-2xl mb-8">
                <h2 className="text-3xl font-bold text-gray-800 text-center mb-4">
                  Step 2: Record Video
                </h2>
                <p className="text-gray-600 text-center mb-8">
                  Record a short video of yourself standing still. OpenCV will
                  detect your body pose and find the best frame for try-on.
                </p>

                <div className="text-center mb-8">
                  <video
                    ref={videoRef}
                    autoPlay
                    muted
                    playsInline
                    className="w-full max-w-2xl h-96 bg-black rounded-2xl mx-auto mb-4"
                  />

                  <div className="space-x-4">
                    {!isRecording ? (
                      <button
                        className="bg-green-500 hover:bg-green-600 text-white font-semibold py-3 px-8 rounded-full transition-all duration-300 transform hover:scale-105"
                        onClick={startVideoRecording}
                      >
                        🎥 Start Recording
                      </button>
                    ) : (
                      <div className="space-y-2">
                        <div className="text-lg font-semibold text-gray-700">
                          Recording: {recordingDuration}s
                        </div>
                        <button
                          className="bg-red-500 hover:bg-red-600 text-white font-semibold py-3 px-8 rounded-full transition-all duration-300 transform hover:scale-105"
                          onClick={stopVideoRecording}
                          disabled={recordingDuration < 4}
                        >
                          ⏹️ Stop Recording{" "}
                          {recordingDuration < 4
                            ? `(${4 - recordingDuration}s left)`
                            : ""}
                        </button>
                      </div>
                    )}
                  </div>
                </div>

                {videoBlob && (
                  <div className="text-center">
                    <h3 className="text-xl font-semibold text-gray-700 mb-4">
                      Recorded Video
                    </h3>
                    <video
                      src={URL.createObjectURL(videoBlob)}
                      controls
                      className="w-full max-w-2xl rounded-2xl mx-auto mb-4"
                    />
                    <button
                      className="bg-blue-500 hover:bg-blue-600 disabled:bg-gray-400 text-white font-semibold py-3 px-8 rounded-full transition-all duration-300 transform hover:scale-105 disabled:cursor-not-allowed"
                      onClick={processVideo}
                      disabled={loading}
                    >
                      {loading ? "Processing..." : "Next: Detect Body Pose"}
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* Step 3: Body Detection Processing (Legacy) */}
        {currentStep === 3 && (
          <div className="bg-white rounded-2xl p-8 shadow-2xl mb-8">
            <h2 className="text-3xl font-bold text-gray-800 text-center mb-4">
              Step 3: Body Detection
            </h2>
            <p className="text-gray-600 text-center mb-8">
              OpenCV is analyzing your video to detect body pose and find the
              best frame for try-on...
            </p>

            <div className="text-center py-12">
              <div className="w-12 h-12 border-4 border-gray-300 border-t-green-500 rounded-full animate-spin mx-auto mb-4"></div>
              <p className="text-gray-600">
                Detecting body pose with OpenCV...
              </p>
              <p className="text-sm text-gray-500 mt-2">
                Looking for frames where all body keypoints are visible
              </p>
            </div>
          </div>
        )}

        {/* Step 4: Try-On */}
        {currentStep === 4 && (
          <div className="bg-white rounded-2xl p-8 shadow-2xl mb-8">
            <h2 className="text-3xl font-bold text-gray-800 text-center mb-4">
              Step 4: Virtual Try-On
            </h2>
            <p className="text-gray-600 text-center mb-8">
              Selected frame with detected body pose and garment ready for
              try-on
            </p>

            <div className="grid lg:grid-cols-3 gap-8 mb-8">
              <div className="text-center bg-gray-50 rounded-xl p-6">
                <h3 className="text-xl font-semibold text-gray-700 mb-4">
                  Detected Body Frame
                </h3>
                {selectedFrame && (
                  <img
                    src={selectedFrame}
                    alt="Selected frame with body detection"
                    className="w-full max-w-xs h-96 object-cover rounded-lg border-2 border-gray-200 mx-auto"
                  />
                )}
              </div>

              <div className="text-center bg-gray-50 rounded-xl p-6">
                <h3 className="text-xl font-semibold text-gray-700 mb-4">
                  Selected Garment
                </h3>
                {selectedGarment &&
                  garments.find((g) => g.id === selectedGarment) && (
                    <img
                      src={
                        garments.find((g) => g.id === selectedGarment)
                          ?.image_url
                      }
                      alt="Selected garment"
                      className="w-full max-w-xs h-96 object-cover rounded-lg border-2 border-gray-200 mx-auto"
                    />
                  )}
              </div>

              <div className="bg-gray-50 rounded-xl p-6">
                <h3 className="text-xl font-semibold text-gray-700 mb-4 text-center">
                  Detection Results
                </h3>
                {realtimeDetectionData ? (
                  <div className="space-y-4">
                    <div className="bg-white rounded-lg p-4 border-l-4 border-green-500">
                      <h4 className="font-semibold text-gray-800 mb-2">
                        Real-Time Confidence
                      </h4>
                      <div className="text-2xl font-bold text-green-600">
                        {(realtimeDetectionData.confidence * 100).toFixed(1)}%
                      </div>
                      <div className="text-sm text-gray-600 mt-2">
                        Detection Mode: Real-time
                      </div>
                    </div>

                    <div className="bg-white rounded-lg p-4 border-l-4 border-blue-500">
                      <h4 className="font-semibold text-gray-800 mb-2">
                        Detection Breakdown
                      </h4>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span>Faces:</span>
                          <span className="font-medium">
                            {realtimeDetectionData.detection_quality.face_count}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span>Bodies:</span>
                          <span className="font-medium">
                            {realtimeDetectionData.detection_quality.body_count}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span>Landmarks:</span>
                          <span className="font-medium">
                            {
                              realtimeDetectionData.detection_quality
                                .landmark_count
                            }
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span>Brightness:</span>
                          <span className="font-medium">
                            {realtimeDetectionData.detection_quality.brightness.toFixed(
                              0
                            )}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                ) : bodyDetectionResult ? (
                  <div className="space-y-4">
                    <div className="bg-white rounded-lg p-4 border-l-4 border-green-500">
                      <h4 className="font-semibold text-gray-800 mb-2">
                        Overall Confidence
                      </h4>
                      <div className="text-2xl font-bold text-green-600">
                        {(bodyDetectionResult.confidence! * 100).toFixed(1)}%
                      </div>
                      {bodyDetectionResult.detection_mode && (
                        <div className="text-sm text-gray-600 mt-2">
                          Detection Mode:{" "}
                          <span className="font-medium">
                            {bodyDetectionResult.detection_mode}
                          </span>
                        </div>
                      )}
                    </div>

                    {bodyDetectionResult.annotations && (
                      <div className="bg-white rounded-lg p-4 border-l-4 border-blue-500">
                        <h4 className="font-semibold text-gray-800 mb-2">
                          Detection Breakdown
                        </h4>
                        <div className="space-y-2 text-sm">
                          <div className="flex justify-between">
                            <span>Face Detection:</span>
                            <span className="font-medium">
                              {(
                                (bodyDetectionResult.annotations
                                  .detection_quality?.face_confidence || 0) *
                                100
                              ).toFixed(1)}
                              %
                            </span>
                          </div>
                          <div className="flex justify-between">
                            <span>Body Detection:</span>
                            <span className="font-medium">
                              {(
                                (bodyDetectionResult.annotations
                                  .detection_quality?.body_confidence || 0) *
                                100
                              ).toFixed(1)}
                              %
                            </span>
                          </div>
                          <div className="flex justify-between">
                            <span>Quality Score:</span>
                            <span className="font-medium">
                              {(
                                (bodyDetectionResult.annotations
                                  .detection_quality?.quality_score || 0) * 100
                              ).toFixed(1)}
                              %
                            </span>
                          </div>
                          <div className="flex justify-between">
                            <span>Image Quality:</span>
                            <span className="font-medium">
                              {(
                                (bodyDetectionResult.annotations
                                  .detection_quality?.brightness_confidence ||
                                  0) +
                                (bodyDetectionResult.annotations
                                  .detection_quality?.contrast_confidence || 0)
                              ).toFixed(1)}
                              %
                            </span>
                          </div>
                        </div>
                      </div>
                    )}

                    <div className="bg-white rounded-lg p-4 border-l-4 border-purple-500">
                      <h4 className="font-semibold text-gray-800 mb-2">
                        Detected Objects
                      </h4>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span>Faces:</span>
                          <span className="font-medium text-green-600">
                            {bodyDetectionResult.annotations?.faces.length || 0}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span>Bodies:</span>
                          <span className="font-medium text-blue-600">
                            {bodyDetectionResult.annotations?.bodies.length ||
                              0}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span>Frame #:</span>
                          <span className="font-medium">
                            {bodyDetectionResult.frame_number || "N/A"}
                          </span>
                        </div>
                        {bodyDetectionResult.annotations?.detection_quality && (
                          <>
                            <div className="flex justify-between">
                              <span>Brightness:</span>
                              <span className="font-medium">
                                {bodyDetectionResult.annotations.detection_quality.brightness?.toFixed(
                                  0
                                ) || "N/A"}
                              </span>
                            </div>
                            <div className="flex justify-between">
                              <span>Contrast:</span>
                              <span className="font-medium">
                                {bodyDetectionResult.annotations.detection_quality.contrast?.toFixed(
                                  0
                                ) || "N/A"}
                              </span>
                            </div>
                          </>
                        )}
                      </div>
                    </div>

                    <div className="bg-white rounded-lg p-4 border-l-4 border-orange-500">
                      <h4 className="font-semibold text-gray-800 mb-2">
                        Legend
                      </h4>
                      <div className="space-y-2 text-sm">
                        <div className="flex items-center">
                          <div className="w-4 h-4 bg-green-500 rounded mr-2"></div>
                          <span>Green: Face Detection</span>
                        </div>
                        <div className="flex items-center">
                          <div className="w-4 h-4 bg-blue-500 rounded mr-2"></div>
                          <span>Blue: Body Detection</span>
                        </div>
                        <div className="flex items-center">
                          <div className="w-4 h-4 bg-white border border-gray-300 rounded mr-2"></div>
                          <span>White: Confidence Score</span>
                        </div>
                      </div>
                    </div>
                  </div>
                ) : null}
              </div>
            </div>

            <div className="text-center">
              <button
                className="bg-orange-500 hover:bg-orange-600 disabled:bg-gray-400 text-white font-semibold py-3 px-8 rounded-full transition-all duration-300 transform hover:scale-105 disabled:cursor-not-allowed"
                onClick={performTryOn}
                disabled={loading}
              >
                {loading ? "Processing Try-On..." : "🎽 Perform Try-On"}
              </button>
            </div>
          </div>
        )}

        {/* Step 5: Results */}
        {currentStep === 5 && tryOnResult && (
          <div className="bg-white rounded-2xl p-8 shadow-2xl mb-8">
            <h2 className="text-3xl font-bold text-gray-800 text-center mb-8">
              Step 5: Try-On Results
            </h2>

            <div className="grid lg:grid-cols-3 gap-8 mb-8">
              <div className="lg:col-span-2 text-center">
                <h3 className="text-xl font-semibold text-gray-700 mb-4">
                  Try-On Result
                </h3>
                <img
                  src={tryOnResult.result_image}
                  alt="Try-on result"
                  className="w-full max-w-lg rounded-2xl shadow-lg mx-auto"
                />
                <p className="text-gray-600 mt-4">{tryOnResult.message}</p>
              </div>

              {tryOnResult.recommendations &&
                tryOnResult.recommendations.length > 0 && (
                  <div className="bg-gray-50 rounded-xl p-6">
                    <h3 className="text-xl font-semibold text-gray-700 mb-4">
                      AI Recommendations
                    </h3>
                    <div className="space-y-4">
                      {tryOnResult.recommendations.map((rec, index) => (
                        <div
                          key={index}
                          className="bg-white rounded-lg p-4 border-l-4 border-green-500"
                        >
                          <h4 className="font-semibold text-gray-800 mb-2">
                            {rec.name}
                          </h4>
                          <p className="text-sm text-gray-600 mb-2">
                            {rec.description}
                          </p>
                          <span className="bg-green-500 text-white px-3 py-1 rounded-full text-xs font-medium">
                            {rec.style_category}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
            </div>

            <div className="text-center">
              <button
                className="bg-purple-500 hover:bg-purple-600 text-white font-semibold py-3 px-8 rounded-full transition-all duration-300 transform hover:scale-105"
                onClick={resetApp}
              >
                🔄 Start Over
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <footer className="text-center py-8 px-4 bg-black/10 backdrop-blur-md mt-8">
        <p className="text-white/80">
          Built for Hack the 6ix 2025 | Powered by AI & OpenCV
        </p>
      </footer>

      {/* API Tester for Development */}
      <ApiTester />
    </div>
  );
}

export default App;
