import { useState } from "react";

interface ApiResponse {
  success?: boolean;
  error?: string;
  status?: number;
  [key: string]: unknown;
}

export default function ApiTester() {
  const [responses, setResponses] = useState<{ [key: string]: ApiResponse }>(
    {}
  );
  const [loading, setLoading] = useState<string | null>(null);

  const API_BASE = "http://localhost:3001";

  const testEndpoint = async (
    endpoint: string,
    method: string = "GET",
    body?: unknown
  ) => {
    setLoading(endpoint);
    try {
      const options: RequestInit = {
        method,
        headers: {},
      };

      if (body) {
        if (body instanceof FormData) {
          options.body = body;
        } else {
          options.headers = { "Content-Type": "application/json" };
          options.body = JSON.stringify(body);
        }
      }

      const response = await fetch(`${API_BASE}${endpoint}`, options);
      const data = await response.json();

      setResponses((prev) => ({
        ...prev,
        [endpoint]: { ...data, status: response.status },
      }));
    } catch (error) {
      setResponses((prev) => ({
        ...prev,
        [endpoint]: {
          error: error instanceof Error ? error.message : "Unknown error",
        },
      }));
    } finally {
      setLoading(null);
    }
  };

  const testHealth = () => testEndpoint("/health");
  const testPresetGarments = () => testEndpoint("/preset-garments");
  const testUserHistory = () => testEndpoint("/user-history/test_user_123");

  const testUploadGarment = () => {
    // Create a simple test image (1x1 pixel)
    const canvas = document.createElement("canvas");
    canvas.width = 1;
    canvas.height = 1;
    const ctx = canvas.getContext("2d");
    if (ctx) {
      ctx.fillStyle = "blue";
      ctx.fillRect(0, 0, 1, 1);
    }

    canvas.toBlob((blob) => {
      if (blob) {
        const formData = new FormData();
        formData.append("garment_image", blob, "test_garment.png");
        formData.append("user_id", "test_user_123");
        formData.append("description", "Test garment from API tester");
        testEndpoint("/upload-garment", "POST", formData);
      }
    });
  };

  const testProcessVideo = () => {
    // Create a simple test video (1x1 pixel, 1 frame)
    const canvas = document.createElement("canvas");
    canvas.width = 1;
    canvas.height = 1;
    const ctx = canvas.getContext("2d");
    if (ctx) {
      ctx.fillStyle = "red";
      ctx.fillRect(0, 0, 1, 1);
    }

    canvas.toBlob((blob) => {
      if (blob) {
        const formData = new FormData();
        formData.append("video_file", blob, "test_video.webm");
        testEndpoint("/process-video", "POST", formData);
      }
    }, "video/webm");
  };

  const testTryOn = () => {
    const data = {
      person_image_path: "/path/to/test/frame.jpg",
      garment_id: "blue_shirt",
      user_id: "test_user_123",
    };
    testEndpoint("/tryon", "POST", data);
  };

  return (
    <div className="bg-white rounded-2xl p-8 shadow-2xl mx-4 mb-8">
      <h2 className="text-2xl font-bold text-gray-800 text-center mb-2">
        🔧 API Endpoint Tester
      </h2>
      <p className="text-gray-600 text-center mb-8">
        Test all backend endpoints from the frontend
      </p>

      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        <div className="bg-gray-50 rounded-xl p-6 border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">
            Health Check
          </h3>
          <button
            onClick={testHealth}
            disabled={loading === "/health"}
            className="w-full py-3 px-4 bg-blue-500 hover:bg-blue-600 disabled:bg-gray-400 text-white font-medium rounded-lg transition-colors duration-200 mb-4"
          >
            {loading === "/health" ? "Testing..." : "Test /health"}
          </button>
          <pre className="bg-gray-100 p-4 rounded-lg text-xs overflow-x-auto max-h-48 overflow-y-auto">
            {JSON.stringify(responses["/health"], null, 2)}
          </pre>
        </div>

        <div className="bg-gray-50 rounded-xl p-6 border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">
            Preset Garments
          </h3>
          <button
            onClick={testPresetGarments}
            disabled={loading === "/preset-garments"}
            className="w-full py-3 px-4 bg-blue-500 hover:bg-blue-600 disabled:bg-gray-400 text-white font-medium rounded-lg transition-colors duration-200 mb-4"
          >
            {loading === "/preset-garments"
              ? "Testing..."
              : "Test /preset-garments"}
          </button>
          <pre className="bg-gray-100 p-4 rounded-lg text-xs overflow-x-auto max-h-48 overflow-y-auto">
            {JSON.stringify(responses["/preset-garments"], null, 2)}
          </pre>
        </div>

        <div className="bg-gray-50 rounded-xl p-6 border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">
            Upload Garment
          </h3>
          <button
            onClick={testUploadGarment}
            disabled={loading === "/upload-garment"}
            className="w-full py-3 px-4 bg-blue-500 hover:bg-blue-600 disabled:bg-gray-400 text-white font-medium rounded-lg transition-colors duration-200 mb-4"
          >
            {loading === "/upload-garment"
              ? "Testing..."
              : "Test /upload-garment"}
          </button>
          <pre className="bg-gray-100 p-4 rounded-lg text-xs overflow-x-auto max-h-48 overflow-y-auto">
            {JSON.stringify(responses["/upload-garment"], null, 2)}
          </pre>
        </div>

        <div className="bg-gray-50 rounded-xl p-6 border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">
            Process Video
          </h3>
          <button
            onClick={testProcessVideo}
            disabled={loading === "/process-video"}
            className="w-full py-3 px-4 bg-blue-500 hover:bg-blue-600 disabled:bg-gray-400 text-white font-medium rounded-lg transition-colors duration-200 mb-4"
          >
            {loading === "/process-video"
              ? "Testing..."
              : "Test /process-video"}
          </button>
          <pre className="bg-gray-100 p-4 rounded-lg text-xs overflow-x-auto max-h-48 overflow-y-auto">
            {JSON.stringify(responses["/process-video"], null, 2)}
          </pre>
        </div>

        <div className="bg-gray-50 rounded-xl p-6 border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">
            Virtual Try-On
          </h3>
          <button
            onClick={testTryOn}
            disabled={loading === "/tryon"}
            className="w-full py-3 px-4 bg-blue-500 hover:bg-blue-600 disabled:bg-gray-400 text-white font-medium rounded-lg transition-colors duration-200 mb-4"
          >
            {loading === "/tryon" ? "Testing..." : "Test /tryon"}
          </button>
          <pre className="bg-gray-100 p-4 rounded-lg text-xs overflow-x-auto max-h-48 overflow-y-auto">
            {JSON.stringify(responses["/tryon"], null, 2)}
          </pre>
        </div>

        <div className="bg-gray-50 rounded-xl p-6 border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">
            User History
          </h3>
          <button
            onClick={testUserHistory}
            disabled={loading === "/user-history/test_user_123"}
            className="w-full py-3 px-4 bg-blue-500 hover:bg-blue-600 disabled:bg-gray-400 text-white font-medium rounded-lg transition-colors duration-200 mb-4"
          >
            {loading === "/user-history/test_user_123"
              ? "Testing..."
              : "Test /user-history"}
          </button>
          <pre className="bg-gray-100 p-4 rounded-lg text-xs overflow-x-auto max-h-48 overflow-y-auto">
            {JSON.stringify(responses["/user-history/test_user_123"], null, 2)}
          </pre>
        </div>
      </div>

      <div className="text-center">
        <button
          onClick={() => {
            testHealth();
            setTimeout(() => testPresetGarments(), 500);
            setTimeout(() => testUserHistory(), 1000);
          }}
          className="bg-green-500 hover:bg-green-600 text-white font-semibold py-3 px-8 rounded-full transition-all duration-300 transform hover:scale-105"
        >
          🚀 Test All Endpoints
        </button>
      </div>
    </div>
  );
}
