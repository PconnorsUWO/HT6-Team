import { useState, useRef, useEffect } from "react";
import ApiTester from "./ApiTester";

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

function App() {
  const [currentStep, setCurrentStep] = useState(1);
  const [garments, setGarments] = useState<Garment[]>([]);
  const [selectedGarment, setSelectedGarment] = useState<string>("");
  const [customGarment, setCustomGarment] = useState<File | null>(null);
  const [videoBlob, setVideoBlob] = useState<Blob | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [selectedFrame, setSelectedFrame] = useState<string>("");
  const [tryOnResult, setTryOnResult] = useState<TryOnResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>("");

  const videoRef = useRef<HTMLVideoElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);

  const API_BASE = "http://127.0.0.1:3001";

  // Load preset garments on component mount
  useEffect(() => {
    fetchPresetGarments();
  }, []);

  const fetchPresetGarments = async () => {
    try {
      const response = await fetch(`${API_BASE}/preset-garments`);
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
      const response = await fetch(`${API_BASE}/upload-garment`, {
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

      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: "video/webm;codecs=vp9",
      });

      const chunks: Blob[] = [];
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunks.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunks, { type: "video/webm" });
        setVideoBlob(blob);
        setCurrentStep(3);
      };

      mediaRecorderRef.current = mediaRecorder;
      mediaRecorder.start();
      setIsRecording(true);
      setError("");
    } catch (err) {
      console.error("Error starting video recording:", err);
      setError(
        "Failed to start video recording. Please check camera permissions."
      );
    }
  };

  const stopVideoRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);

      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop());
      }
    }
  };

  const processVideo = async () => {
    if (!videoBlob) return;

    setLoading(true);
    setError("");

    try {
      const formData = new FormData();
      formData.append("video_file", videoBlob, "recording.webm");

      const response = await fetch(`${API_BASE}/process-video`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      if (data.success) {
        // For testing, we'll simulate a frame selection
        setSelectedFrame(
          "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k="
        );
        setCurrentStep(4);
      } else {
        setError(data.error || "Failed to process video");
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
      const formData = new FormData();
      formData.append("person_image_path", selectedFrame);
      formData.append("garment_id", selectedGarment);
      formData.append("user_id", "test_user_123");

      const response = await fetch(`${API_BASE}/tryon`, {
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
    setTryOnResult(null);
    setError("");
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-500 via-purple-500 to-pink-500 font-sans">
      {/* Header */}
      <header className="text-center py-8 px-4 bg-black/10 backdrop-blur-md">
        <h1 className="text-4xl md:text-5xl font-bold text-white mb-2 drop-shadow-lg">
          🎽 Virtual Try-On App
        </h1>
        <p className="text-lg text-white/90">
          AI-Powered Clothing Try-On with Video Processing
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
              {step === 2 && "2. Video Recording"}
              {step === 3 && "3. Frame Analysis"}
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
                Next: Start Video Recording
              </button>
            </div>
          </div>
        )}

        {/* Step 2: Video Recording */}
        {currentStep === 2 && (
          <div className="bg-white rounded-2xl p-8 shadow-2xl mb-8">
            <h2 className="text-3xl font-bold text-gray-800 text-center mb-4">
              Step 2: Record Video
            </h2>
            <p className="text-gray-600 text-center mb-8">
              Record a short video of yourself standing still. The AI will find
              the best frame for try-on.
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
                  <button
                    className="bg-red-500 hover:bg-red-600 text-white font-semibold py-3 px-8 rounded-full transition-all duration-300 transform hover:scale-105"
                    onClick={stopVideoRecording}
                  >
                    ⏹️ Stop Recording
                  </button>
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
                  {loading ? "Processing..." : "Next: Analyze Video"}
                </button>
              </div>
            )}
          </div>
        )}

        {/* Step 3: Frame Analysis */}
        {currentStep === 3 && (
          <div className="bg-white rounded-2xl p-8 shadow-2xl mb-8">
            <h2 className="text-3xl font-bold text-gray-800 text-center mb-4">
              Step 3: Video Analysis
            </h2>
            <p className="text-gray-600 text-center mb-8">
              AI is analyzing your video to find the best frame for try-on...
            </p>

            <div className="text-center py-12">
              <div className="w-12 h-12 border-4 border-gray-300 border-t-green-500 rounded-full animate-spin mx-auto mb-4"></div>
              <p className="text-gray-600">
                Processing video with TwelveLabs...
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
              Selected frame and garment ready for try-on
            </p>

            <div className="grid md:grid-cols-2 gap-8 mb-8">
              <div className="text-center bg-gray-50 rounded-xl p-6">
                <h3 className="text-xl font-semibold text-gray-700 mb-4">
                  Selected Frame
                </h3>
                {selectedFrame && (
                  <img
                    src={selectedFrame}
                    alt="Selected frame"
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
          Built for Hack the 6ix 2025 | Powered by AI
        </p>
      </footer>

      {/* API Tester for Development */}
      <ApiTester />
    </div>
  );
}

export default App;
