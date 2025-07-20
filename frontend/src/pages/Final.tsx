import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import {
  ArrowLeft,
  ChevronLeft,
  ChevronRight,
  Sparkles,
  Home,
  Loader2,
  Camera,
} from "lucide-react";
import { useNavigate, useLocation } from "react-router-dom";
import { toast } from "sonner";

// Define interfaces for our data
interface SelectedItem {
  name: string;
  category: string;
  image_url: string;
  price: number;
  desc: string;
}

interface TryOnResult {
  success: boolean;
  result_id: string;
  result_image: string;
  public_url: string;
  category: string;
  garment_description: string;
  garment_url?: string;
  api_provider?: string;
  recommendations?: {
    item: SelectedItem;
    reason: string;
    score: number;
  }[];
  message: string;
}

interface TryOnState {
  selectedItems?: SelectedItem[];
  userPhoto?: string; // base64 image data from body detection
  detectionData?: {
    confidence: number;
    frameCount: number;
    detectionQuality: {
      face_count: number;
      body_count: number;
      landmark_count: number;
      brightness: number;
    } | null;
  };
}

const Final = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [currentCategory, setCurrentCategory] = useState("shirt");
  const [recommendationIndex, setRecommendationIndex] = useState(0);
  const [loading, setLoading] = useState(false);
  const [tryonResult, setTryonResult] = useState<TryOnResult | null>(null);
  const [currentTryonIndex, setCurrentTryonIndex] = useState(0);

  // Get state passed from previous pages
  const tryonState = location.state as TryOnState;
  const selectedItems = tryonState?.selectedItems || [];
  const userPhoto = tryonState?.userPhoto;
  const detectionData = tryonState?.detectionData;

  useEffect(() => {
    // Check if we have both selected items and user photo
    if (selectedItems.length > 0 && userPhoto) {
      console.log("🎯 Starting try-on with captured user photo");
      console.log(
        `📊 Detection confidence: ${detectionData?.confidence || "unknown"}`
      );
      performTryOnForSelectedItems();
    } else if (selectedItems.length > 0 && !userPhoto) {
      toast.warning("No user photo available. Please capture a photo first.");
      console.warn("⚠️ No user photo provided for try-on");
    }
  }, [selectedItems, userPhoto]);

  const performTryOnForSelectedItems = async () => {
    if (selectedItems.length === 0) {
      toast.error("No items selected for try-on");
      return;
    }

    setLoading(true);

    try {
      // Try on the selected item using its image URL from the catalogue
      const itemToTryOn = selectedItems[currentTryonIndex];

      if (!userPhoto) {
        throw new Error("No user photo available for try-on");
      }

      // Convert base64 data URL to a file for upload
      const base64Data = userPhoto.replace(/^data:image\/[a-z]+;base64,/, "");
      const byteCharacters = atob(base64Data);
      const byteNumbers = new Array(byteCharacters.length);
      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
      }
      const byteArray = new Uint8Array(byteNumbers);
      const blob = new Blob([byteArray], { type: "image/jpeg" });

      // Convert relative URL to absolute URL for the backend
      const garmentUrl = itemToTryOn.image_url.startsWith("http")
        ? itemToTryOn.image_url
        : `http://localhost:8080${itemToTryOn.image_url}`;

      // Prepare form data for the tryon API
      const formData = new FormData();
      formData.append("person_image", blob, "user_photo.jpg");
      formData.append("garment_url", garmentUrl);
      formData.append("garment_description", itemToTryOn.desc);
      formData.append("user_id", "user_123"); // In production, use actual user ID

      console.log(`🔄 Starting try-on for: ${itemToTryOn.name}`);
      console.log(`🔗 Garment URL: ${garmentUrl}`);
      toast.info(`Trying on: ${itemToTryOn.name}...`);

      // Make the API call to the tryon endpoint
      const response = await fetch("http://127.0.0.1:5000/api/tryon", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error(
          `❌ HTTP ${response.status}: ${response.statusText}`,
          errorText
        );
        throw new Error(
          `Try-on API error: ${response.status} - ${response.statusText}`
        );
      }

      const data: TryOnResult = await response.json();

      console.log("📥 Try-on API response:", data);

      if (data.success) {
        setTryonResult(data);
        toast.success(`Try-on completed for ${itemToTryOn.name}!`);
        console.log("✅ Try-on successful!");
        console.log(
          `🖼️ Result image will be served at: http://127.0.0.1:5000/${data.result_image}`
        );
      } else {
        console.error("❌ Try-on API returned failure:", data);
        throw new Error(data.message || "Try-on failed");
      }
    } catch (error) {
      console.error("Try-on error:", error);
      toast.error(
        `Try-on failed: ${
          error instanceof Error ? error.message : "Unknown error"
        }`
      );

      // Show fallback UI
      setTryonResult(null);
    } finally {
      setLoading(false);
    }
  };

  const tryNextItem = () => {
    if (currentTryonIndex < selectedItems.length - 1) {
      setCurrentTryonIndex((prev) => prev + 1);
      setTryonResult(null); // Clear current result
      performTryOnForSelectedItems(); // Try on next item
    }
  };

  const tryPreviousItem = () => {
    if (currentTryonIndex > 0) {
      setCurrentTryonIndex((prev) => prev - 1);
      setTryonResult(null); // Clear current result
      performTryOnForSelectedItems(); // Try on previous item
    }
  };

  // Fallback recommendations for when try-on is not available
  const recommendations = [
    {
      title: "Classic Sophistication",
      description:
        "Try pairing this classic white button-down with dark chinos for a sophisticated casual look. The clean lines complement your features perfectly.",
      image: "/lovable-uploads/47ddf8ec-e767-4383-ba70-1d2b84565232.png",
      tags: ["Casual", "Professional", "Versatile"],
    },
    {
      title: "Modern Edge",
      description:
        "A relaxed v-neck tee in soft cotton creates an effortless, approachable style. Perfect for weekend outings or casual meetings.",
      image: "/lovable-uploads/47ddf8ec-e767-4383-ba70-1d2b84565232.png",
      tags: ["Relaxed", "Weekend", "Comfortable"],
    },
    {
      title: "Smart Casual",
      description:
        "Elevate your look with a well-fitted polo shirt. This timeless piece bridges the gap between casual and formal beautifully.",
      image: "/lovable-uploads/47ddf8ec-e767-4383-ba70-1d2b84565232.png",
      tags: ["Smart Casual", "Timeless", "Versatile"],
    },
  ];

  const categories = [
    { id: "shirt", label: "Shirts", icon: "👕" },
    { id: "pants", label: "Pants", icon: "👖" },
    { id: "dresses", label: "Dresses", icon: "👗" },
    { id: "accessories", label: "Accessories", icon: "👜" },
  ];

  const alternativeItems = {
    shirt: [
      { name: "Linen Shirt", color: "White", price: "$89", match: "95%" },
      { name: "Cotton Polo", color: "Navy", price: "$65", match: "88%" },
      {
        name: "Oxford Button-down",
        color: "Light Blue",
        price: "$95",
        match: "92%",
      },
    ],
    pants: [
      { name: "Slim Chinos", color: "Khaki", price: "$75", match: "90%" },
      { name: "Dress Pants", color: "Charcoal", price: "$120", match: "87%" },
      { name: "Dark Jeans", color: "Indigo", price: "$95", match: "85%" },
    ],
    dresses: [
      { name: "Midi Dress", color: "Black", price: "$140", match: "93%" },
      { name: "Wrap Dress", color: "Navy", price: "$110", match: "89%" },
      { name: "Shirt Dress", color: "White", price: "$95", match: "91%" },
    ],
    accessories: [
      { name: "Leather Belt", color: "Brown", price: "$45", match: "96%" },
      { name: "Canvas Bag", color: "Tan", price: "$85", match: "88%" },
      { name: "Watch", color: "Silver", price: "$220", match: "94%" },
    ],
  };

  const currentRecommendation = recommendations[recommendationIndex];
  const currentAlternatives =
    alternativeItems[currentCategory as keyof typeof alternativeItems];
  const currentItem = selectedItems[currentTryonIndex];

  const nextRecommendation = () => {
    setRecommendationIndex((prev) => (prev + 1) % recommendations.length);
  };

  const prevRecommendation = () => {
    setRecommendationIndex(
      (prev) => (prev - 1 + recommendations.length) % recommendations.length
    );
  };

  // Add useEffect to start the live camera preview
  useEffect(() => {
    const video = document.getElementById("livePreviewVideo") as HTMLVideoElement | null;
    if (video) {
      navigator.mediaDevices.getUserMedia({ video: { aspectRatio: 9 / 16 } })
        .then((stream) => {
          video.srcObject = stream;
          video.play();
        })
        .catch((err) => {
          console.error("Failed to start live camera preview", err);
        });
    }
    return () => {
      if (video && video.srcObject) {
        const tracks = (video.srcObject as MediaStream).getTracks();
        tracks.forEach((track) => track.stop());
        video.srcObject = null;
      }
    };
  }, []);

  return (
    <div className="min-h-screen bg-gradient-background relative overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute inset-0 opacity-20">
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
            Return to Homepage
          </Button>

          <div className="flex items-center gap-2 text-white">
            <Sparkles className="w-5 h-5 text-primary-glow" />
            <h1 className="text-xl font-semibold">Virtual Try-On Results</h1>
          </div>
        </div>

        {/* Current Item Info */}
        {currentItem && (
          <div className="text-center mb-6 text-white animate-fade-in">
            <h2 className="text-2xl font-bold mb-2">
              Trying On: {currentItem.name}
            </h2>
            <p className="text-white/80">{currentItem.desc}</p>
            <div className="flex justify-center gap-4 mt-4">
              <Button
                variant="ghost"
                size="sm"
                onClick={tryPreviousItem}
                disabled={currentTryonIndex === 0 || loading}
                className="text-white hover:bg-white/10"
              >
                <ChevronLeft className="w-4 h-4" />
                Previous Item
              </Button>
              <span className="px-4 py-2 bg-white/10 rounded-lg text-sm">
                {currentTryonIndex + 1} of {selectedItems.length}
              </span>
              <Button
                variant="ghost"
                size="sm"
                onClick={tryNextItem}
                disabled={
                  currentTryonIndex === selectedItems.length - 1 || loading
                }
                className="text-white hover:bg-white/10"
              >
                Next Item
                <ChevronRight className="w-4 h-4" />
              </Button>
            </div>
          </div>
        )}

        <div className="grid lg:grid-cols-3 gap-3">
          {/* Left Panel - Recommendation */}
          <div className="space-y-6">
            <Card className="p-6 bg-white/10 backdrop-blur-md border-white/20 text-white animate-scale-in">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-primary-glow" />
                  Style Recommendations
                </h2>
                <div className="flex gap-1">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={prevRecommendation}
                    className="text-white hover:bg-white/10"
                  >
                    <ChevronLeft className="w-4 h-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={nextRecommendation}
                    className="text-white hover:bg-white/10"
                  >
                    <ChevronRight className="w-4 h-4" />
                  </Button>
                </div>
              </div>

              <div className="space-y-4">
                <h3 className="text-lg font-medium text-primary-glow">
                  {currentRecommendation.title}
                </h3>

                <p className="text-sm text-white/90 leading-relaxed">
                  {currentRecommendation.description}
                </p>

                <div className="flex flex-wrap gap-2">
                  {currentRecommendation.tags.map((tag) => (
                    <span
                      key={tag}
                      className="px-3 py-1 bg-white/10 rounded-full text-xs border border-white/20"
                    >
                      {tag}
                    </span>
                  ))}
                </div>

                <div className="flex items-center justify-between text-xs text-white/70">
                  <span>
                    {recommendationIndex + 1} of {recommendations.length}
                  </span>
                  <span>AI Styled</span>
                </div>
              </div>
            </Card>

            {/* Try-On Status */}
            <Card
              className="p-4 bg-white/10 backdrop-blur-md border-white/20 text-white animate-scale-in"
              style={{ animationDelay: "0.2s" }}
            >
              <h4 className="font-medium mb-3 text-sm flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-primary-glow" />
                Try-On Status
              </h4>
              {loading ? (
                <div className="flex items-center gap-3">
                  <Loader2 className="w-4 h-4 animate-spin text-primary-glow" />
                  <span className="text-sm">Processing try-on...</span>
                </div>
              ) : tryonResult ? (
                <div className="space-y-2">
                  <div className="flex items-center gap-3">
                    <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                    <span className="text-sm">
                      Try-on completed successfully!
                    </span>
                  </div>
                  <div className="space-y-1 text-xs text-white/70">
                    <div className="flex justify-between">
                      <span>Category:</span>
                      <span className="capitalize">
                        {tryonResult.category.replace("_", " ")}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span>Provider:</span>
                      <span className="capitalize">
                        {tryonResult.api_provider || "segmind"}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span>Result ID:</span>
                      <span className="font-mono">
                        {tryonResult.result_id.slice(0, 8)}...
                      </span>
                    </div>
                    <div className="mt-2 p-2 bg-green-500/10 rounded border border-green-500/20">
                      <div className="text-green-400 text-xs font-medium">
                        ✓ Image ready at:
                      </div>
                      <div className="text-xs font-mono break-all">
                        {tryonResult.result_image}
                      </div>
                    </div>
                  </div>
                </div>
              ) : userPhoto ? (
                <div className="flex items-center gap-3">
                  <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                  <span className="text-sm">Ready for try-on</span>
                </div>
              ) : (
                <div className="flex items-center gap-3">
                  <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                  <span className="text-sm">No user photo available</span>
                </div>
              )}
            </Card>

            {/* Detection Quality Info */}
            {detectionData && (
              <Card
                className="p-4 bg-white/10 backdrop-blur-md border-white/20 text-white animate-scale-in"
                style={{ animationDelay: "0.3s" }}
              >
                <h4 className="font-medium mb-3 text-sm flex items-center gap-2">
                  📊 Detection Quality
                </h4>
                <div className="space-y-2 text-xs">
                  <div className="flex justify-between">
                    <span>Confidence:</span>
                    <span className="text-primary-glow font-medium">
                      {(detectionData.confidence * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Frames processed:</span>
                    <span>{detectionData.frameCount}</span>
                  </div>
                  {detectionData.detectionQuality && (
                    <>
                      <div className="flex justify-between">
                        <span>Bodies detected:</span>
                        <span>{detectionData.detectionQuality.body_count}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Faces detected:</span>
                        <span>{detectionData.detectionQuality.face_count}</span>
                      </div>
                    </>
                  )}
                </div>
              </Card>
            )}
          </div>

          {/* Center - Main Image */}
          <div
            className="flex items-center justify-center animate-scale-in"
            style={{ animationDelay: "0.3s" }}
          >
            <div className="relative w-full h-full">
              <div className="absolute inset-0 bg-gradient-primary rounded-2xl blur-xl opacity-30 scale-110"></div>
              <Card
                className="relative overflow-hidden bg-white/5 backdrop-blur-sm border-white/20 p-2 h-full"
                style={{
                  aspectRatio: "9/16",
                }}
              >
                {loading ? (
                  <div className="w-full max-w-sm h-full flex items-center justify-center bg-white/10 rounded-xl">
                    <div className="text-center text-white">
                      <Loader2 className="w-12 h-12 animate-spin mx-auto mb-4 text-primary-glow" />
                      <p className="text-sm">Generating try-on image...</p>
                      <p className="text-xs text-white/70 mt-2">
                        This may take 30-60 seconds
                      </p>
                    </div>
                  </div>
                ) : tryonResult ? (
                  <div className="relative p-3 w-full h-full">
                    <img
                      src={`http://127.0.0.1:5000/${tryonResult.result_image}`}
                      alt={`Virtual try-on result for ${
                        selectedItems[currentTryonIndex]?.name ||
                        "selected item"
                      }`}
                      className="w-full h-full object- rounded-xl"
                      style={{
                        aspectRatio: "9/16",
                      }}
                      onLoad={() => {
                        console.log(
                          "✅ Try-on result image loaded successfully"
                        );
                      }}
                      onError={(e) => {
                        console.error(
                          "❌ Failed to load try-on result image:",
                          `http://127.0.0.1:5000/${tryonResult.result_image}`
                        );
                        console.error("Try-on result data:", tryonResult);
                        // Show error message instead of fallback
                        const target = e.target as HTMLImageElement;
                        target.style.display = "none";
                        // Create error message element
                        const errorDiv =
                          target.parentElement?.querySelector(".image-error");
                        if (!errorDiv) {
                          const error = document.createElement("div");
                          error.className =
                            "image-error w-full h-full flex items-center justify-center bg-red-500/20 rounded-xl border border-red-500/30";
                          error.innerHTML = `
                            <div class="text-center text-white">
                              <div class="text-red-400 mb-2">Failed to load try-on result</div>
                              <div class="text-xs text-white/70">Image path: ${tryonResult.result_image}</div>
                              <button class="mt-2 px-3 py-1 bg-red-500/30 rounded text-xs" onclick="location.reload()">Retry</button>
                            </div>
                          `;
                          target.parentElement?.appendChild(error);
                        }
                      }}
                    />
                    {/* Success indicator */}
                    <div className="absolute top-2 right-2 bg-green-500/80 text-white px-2 py-1 rounded-full text-xs flex items-center gap-1">
                      <div className="w-2 h-2 bg-green-300 rounded-full animate-pulse"></div>
                      AI Generated
                    </div>
                    {/* Image info overlay */}
                    <div className="absolute bottom-2 left-2 bg-black/50 text-white px-2 py-1 rounded text-xs">
                      Result ID: {tryonResult.result_id.slice(0, 8)}...
                    </div>
                    {/* Download button */}
                    <div className="absolute bottom-2 right-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        className="bg-black/50 text-white hover:bg-black/70 text-xs px-2 py-1 h-auto"
                        onClick={() => {
                          const link = document.createElement("a");
                          link.href = `http://127.0.0.1:5000/${tryonResult.result_image}`;
                          link.download = `tryon_result_${tryonResult.result_id.slice(
                            0,
                            8
                          )}.png`;
                          link.click();
                          toast.success("Downloading try-on result!");
                        }}
                      >
                        💾 Save
                      </Button>
                    </div>
                  </div>
                ) : (
                  <div className="w-full max-w-sm h-full flex items-center justify-center bg-white/10 rounded-xl">
                    <div className="text-center text-white">
                      {userPhoto ? (
                        <>
                          <Sparkles className="w-12 h-12 mx-auto mb-4 text-primary-glow" />
                          <p className="text-sm">Ready for virtual try-on</p>
                          <Button
                            onClick={performTryOnForSelectedItems}
                            variant="glass"
                            className="mt-4"
                            disabled={selectedItems.length === 0}
                          >
                            Try On Now
                          </Button>
                        </>
                      ) : (
                        <>
                          <Camera className="w-12 h-12 mx-auto mb-4 text-white/50" />
                          <p className="text-sm mb-2">No photo captured</p>
                          <p className="text-xs text-white/70 mb-4">
                            Please capture your photo first
                          </p>
                          <Button
                            onClick={() => navigate("/take_photo")}
                            variant="glass"
                            className="mt-4"
                          >
                            Capture Photo
                          </Button>
                        </>
                      )}
                    </div>
                  </div>
                )}
                <div className="absolute top-4 left-4">
                  <span className="px-3 py-1 bg-black/50 backdrop-blur-sm text-white text-xs rounded-full">
                    {tryonResult ? "Virtual Try-On Result" : "Try-On Preview"}
                  </span>
                </div>
              </Card>
            </div>
          </div>

          {/* Right Panel - Live Camera Preview */}
          <div
            className="flex items-center justify-center animate-slide-in-right"
            style={{ animationDelay: "0.4s" }}
          >
            <div className="relative p-3 w-full h-full">
              <div className="relative bg-black rounded-2xl overflow-hidden mb-4 w-full h-full" style={{ aspectRatio: '9/16' }}>
                <video
                  autoPlay
                  muted
                  playsInline
                  className="w-full h-full object-contain rounded-2xl"
                  style={{ aspectRatio: '9/16' }}
                  id="livePreviewVideo"
                />
                <div className="absolute top-4 left-4">
                  <span className="px-3 py-1 bg-black/50 backdrop-blur-sm text-white text-xs rounded-full">
                    Live Preview
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Final;
