import React, { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Home,
  Sparkles,
  ShoppingBag,
  ArrowRight,
  Loader2,
  Star,
  Tag,
  Shirt,
} from "lucide-react";
import { toast } from "sonner";
import {
  getStyleRecommendations,
  getQuickRecommendations,
  createQuickRecommendationRequest,
  CatalogueItem,
  RecommendationItem,
  StyleRecommendationsResponse,
  QuickRecommendationsResponse,
  isApiError,
  getErrorMessage,
} from "@/lib/recommendations/api";
import {
  UserProfile,
  tedProfileData,
} from "@/lib/recommendations/const/userprofile";
import { RecommendationsContext } from "@/lib/recommendations/const/catalogue";

interface RecommendationsData {
  top_10: RecommendationItem[];
}

const PickClothes: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [loading, setLoading] = useState(true);
  const [recommendations, setRecommendations] = useState<RecommendationItem[]>(
    []
  );
  const [selectedCategory, setSelectedCategory] = useState<string>("all");
  const [selectedItems, setSelectedItems] = useState<Set<string>>(new Set());
  const [isRetrying, setIsRetrying] = useState(false);

  // Get user photo and detection data from previous step
  const locationState = location.state as {
    userPhoto?: string;
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
  };
  const userPhoto = locationState?.userPhoto;
  const detectionData = locationState?.detectionData;

  useEffect(() => {
    fetchRecommendations();
  }, []);

  const retryFetchRecommendations = async () => {
    setIsRetrying(true);
    await fetchRecommendations();
    setIsRetrying(false);
  };

  const fetchRecommendations = async () => {
    try {
      setLoading(true);

      // Use the sample user profile (Ted's profile)
      const userProfile: UserProfile = tedProfileData;

      try {
        // Try to get style recommendations using the full API
        // The API will automatically use the complete catalogue from RecommendationsContext
        const response: StyleRecommendationsResponse =
          await getStyleRecommendations(userProfile);

        if (response.success && response.recommendations) {
          // Transform API response to match our component's expected format
          // Handle both nested (final-output.top_10) and direct (top_10) response structures
          const recommendationsData =
            response.recommendations["final-output"]?.top_10 ||
            response.recommendations.top_10 ||
            [];

          console.log("recommendationsData", response.recommendations);

          const formattedRecommendations: RecommendationItem[] =
            recommendationsData.map(
              (rec: {
                item?: CatalogueItem;
                category?: string;
                desc?: string;
                image_url?: string;
                name?: string;
                price?: number;
                sizes_available?: string[];
                reason?: string;
                score?: number;
              }) => ({
                item: {
                  category: rec.item?.category || rec.category || "general",
                  desc:
                    rec.item?.desc || rec.desc || "No description available",
                  image_url:
                    rec.item?.image_url ||
                    // temporarily use image_url from the catalogue
                    RecommendationsContext.find(
                      (item) => item.name === rec.item?.name
                    )?.image_url ||
                    rec.image_url ||
                    `https://picsum.photos/seed/${
                      rec.item?.name || rec.name || "item"
                    }/600/800`,
                  name: rec.item?.name || rec.name || "Unknown Item",
                  price: rec.item?.price || rec.price || 0,
                  sizes_available: rec.item?.sizes_available ||
                    rec.sizes_available || ["S", "M", "L"],
                },
                reason:
                  rec.reason || "Recommended based on your style preferences",
                score: rec.score || 85,
              })
            ) || [];

          // Sort recommendations by score/confidence (highest first)
          const sortedRecommendations = formattedRecommendations.sort(
            (a, b) => b.score - a.score
          );
          setRecommendations(sortedRecommendations);
          toast.success("Style recommendations loaded successfully!");
        } else {
          throw new Error(response.message || "Failed to get recommendations");
        }
      } catch (firstError) {
        const apiError = firstError;
        console.warn(
          "Style recommendations API failed, trying quick recommendations:",
          apiError
        );

        try {
          // Fallback to quick recommendations
          const quickRequest = createQuickRecommendationRequest(userProfile);
          const quickResponse: QuickRecommendationsResponse =
            await getQuickRecommendations(quickRequest);

          if (quickResponse.success && quickResponse.recommendations) {
            // Transform quick recommendations response
            // Handle both nested (final-output.top_10) and direct (top_10) response structures
            const recommendationsData =
              quickResponse.recommendations["final-output"]?.top_10 ||
              quickResponse.recommendations.top_10 ||
              [];

            const formattedRecommendations: RecommendationItem[] =
              recommendationsData.map(
                (rec: {
                  item?: CatalogueItem;
                  category?: string;
                  desc?: string;
                  image_url?: string;
                  name?: string;
                  price?: number;
                  sizes_available?: string[];
                  reason?: string;
                  score?: number;
                }) => ({
                  item: {
                    category: rec.item?.category || rec.category || "general",
                    desc:
                      rec.item?.desc || rec.desc || "No description available",
                    image_url:
                      rec.item?.image_url ||
                      rec.image_url ||
                      `https://picsum.photos/seed/${
                        rec.item?.name || rec.name || "item"
                      }/600/800`,
                    name: rec.item?.name || rec.name || "Unknown Item",
                    price: rec.item?.price || rec.price || 0,
                    sizes_available: rec.item?.sizes_available ||
                      rec.sizes_available || ["S", "M", "L"],
                  },
                  reason:
                    rec.reason || "Recommended based on your style preferences",
                  score: rec.score || 85,
                })
              ) || [];

            // Sort recommendations by score/confidence (highest first)
            const sortedRecommendations = formattedRecommendations.sort(
              (a, b) => b.score - a.score
            );
            setRecommendations(sortedRecommendations);
            toast.success("Quick recommendations loaded successfully!");
          } else {
            throw new Error(
              quickResponse.message || "Failed to get quick recommendations"
            );
          }
        } catch (secondError) {
          const quickError = secondError;
          console.error(
            "Both API methods failed, using fallback from catalog:",
            quickError
          );

          // Final fallback: use actual catalog items from RecommendationsContext
          // Convert catalog items to recommendation format
          const fallbackData: RecommendationItem[] =
            RecommendationsContext.slice(0, 10).map((item, index) => ({
              item: {
                category: item.category || "general",
                desc: item.desc,
                image_url:
                  item.image_url ||
                  `https://picsum.photos/seed/${item.name}/600/800`,
                name: item.name,
                price: item.price,
                sizes_available: item.sizes_available,
              },
              reason: `Featured ${
                item.category || "item"
              } from our curated collection`,
              score: 85 + index * 2, // Vary scores slightly
            }));

          // Sort fallback recommendations by score/confidence (highest first)
          const sortedFallbackData = fallbackData.sort(
            (a, b) => b.score - a.score
          );
          setRecommendations(sortedFallbackData);
          toast.warning(
            "Using featured items from catalog. AI recommendations unavailable."
          );
        }
      }
    } catch (error) {
      console.error("Failed to fetch recommendations:", error);
      toast.error(`Failed to load recommendations: ${getErrorMessage(error)}`);

      // Even in case of complete failure, show some items from the actual catalog
      const fallbackData: RecommendationItem[] = RecommendationsContext.slice(
        0,
        6
      ).map((item, index) => ({
        item: {
          category: item.category || "general",
          desc: item.desc,
          image_url:
            item.image_url || `https://picsum.photos/seed/${item.name}/600/800`,
          name: item.name,
          price: item.price,
          sizes_available: item.sizes_available,
        },
        reason: "Featured item from our collection",
        score: 80 + index,
      }));
      // Sort final fallback recommendations by score/confidence (highest first)
      const sortedFinalFallbackData = fallbackData.sort(
        (a, b) => b.score - a.score
      );
      setRecommendations(sortedFinalFallbackData);
    } finally {
      setLoading(false);
    }
  };

  const categories = [
    { id: "all", label: "All Items", icon: ShoppingBag },
    { id: "shirts", label: "Shirts", icon: Shirt },
    { id: "pants", label: "Pants", icon: Tag },
  ];

  const filteredRecommendations =
    selectedCategory === "all"
      ? recommendations
      : recommendations.filter((rec) => rec.item.category === selectedCategory);
  console.log("filteredRecommendations", filteredRecommendations);
  const toggleItemSelection = (itemName: string) => {
    const newSelected = new Set(selectedItems);
    if (newSelected.has(itemName)) {
      newSelected.delete(itemName);
    } else {
      newSelected.add(itemName);
    }
    setSelectedItems(newSelected);
  };

  const proceedToFinal = () => {
    if (selectedItems.size === 0) {
      toast.error("Please select at least one item to continue");
      return;
    }

    // Prepare selected items data to pass to Final page
    const selectedItemsData = recommendations
      .filter((rec) => selectedItems.has(rec.item.name))
      .map((rec) => ({
        name: rec.item.name,
        category: rec.item.category,
        image_url: rec.item.image_url,
        price: rec.item.price,
        desc: rec.item.desc,
      }));

    toast.success(`Selected ${selectedItems.size} items for your wardrobe!`);

    // Navigate to final page with selected items data and user photo
    navigate("/final", {
      state: {
        selectedItems: selectedItemsData,
        userPhoto: userPhoto, // Pass the actual captured user photo
        detectionData: detectionData, // Pass detection metadata
      },
    });
  };

  if (loading) {
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

        <div className="relative z-10 min-h-screen flex items-center justify-center">
          <Card className="bg-white/10 backdrop-blur-md border-white/20 text-white max-w-md mx-auto">
            <CardContent className="p-8 text-center">
              <div className="w-16 h-16 mx-auto mb-6 bg-primary/20 rounded-full flex items-center justify-center">
                <Loader2 className="w-8 h-8 text-primary-glow animate-spin" />
              </div>
              <h2 className="text-2xl font-bold text-white mb-4">
                Curating Your Perfect Style
              </h2>
              <p className="text-white/80 mb-6">
                Our AI stylist is analyzing your preferences and selecting the
                best clothing recommendations from our API...
              </p>
              <div className="space-y-2">
                <div className="w-full bg-white/20 rounded-full h-2">
                  <div className="bg-gradient-to-r from-primary to-primary-glow h-2 rounded-full animate-pulse w-3/4"></div>
                </div>
                <p className="text-sm text-white/60">This may take a moment</p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

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
            <h1 className="text-xl font-semibold">AI Style Recommendations</h1>
          </div>

          <div className="flex items-center gap-3">
            <Badge
              variant="secondary"
              className="bg-primary/20 text-primary-glow border-primary-glow/30"
            >
              {recommendations.length} items found
            </Badge>
            {userPhoto && detectionData && (
              <Badge
                variant="secondary"
                className="bg-green-500/20 text-green-400 border-green-400/30"
                title={`Photo captured with ${(
                  detectionData.confidence * 100
                ).toFixed(1)}% confidence`}
              >
                📸 Photo captured ({(detectionData.confidence * 100).toFixed(0)}
                %)
              </Badge>
            )}
          </div>
        </div>

        {/* Category Filter */}
        <Card className="bg-white/10 backdrop-blur-md border-white/20 mb-8">
          <CardContent className="p-6">
            <h3 className="text-white font-semibold mb-4">
              Filter by Category
            </h3>
            <div className="flex flex-wrap gap-3">
              {categories.map((category) => {
                const IconComponent = category.icon;
                return (
                  <Button
                    key={category.id}
                    variant={
                      selectedCategory === category.id ? "hero" : "glass"
                    }
                    onClick={() => setSelectedCategory(category.id)}
                    className="flex items-center gap-2"
                  >
                    <IconComponent className="w-4 h-4" />
                    {category.label}
                  </Button>
                );
              })}
            </div>
          </CardContent>
        </Card>

        {/* Recommendations Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {filteredRecommendations.map((recommendation, index) => {
            const { item, reason, score } = recommendation;
            const isSelected = selectedItems.has(item.name);

            return (
              <Card
                key={index}
                className={`bg-white/10 backdrop-blur-md border-white/20 text-white hover:bg-white/15 transition-all duration-300 cursor-pointer transform hover:scale-105 ${
                  isSelected ? "ring-2 ring-primary-glow bg-primary/20" : ""
                }`}
                onClick={() => toggleItemSelection(item.name)}
              >
                <div className="relative">
                  <img
                    src={item.image_url}
                    alt={item.name}
                    className="w-full h-64 object-cover rounded-t-lg"
                  />
                  <div className="absolute top-4 right-4 flex items-center gap-2">
                    <Badge className="bg-primary-glow/80 text-white border-0">
                      <Star className="w-3 h-3 mr-1" />
                      {score}%
                    </Badge>
                    <Badge
                      variant="secondary"
                      className="bg-black/50 text-white border-0 capitalize"
                    >
                      {item.category}
                    </Badge>
                  </div>
                  {isSelected && (
                    <div className="absolute inset-0 bg-primary-glow/20 rounded-t-lg flex items-center justify-center">
                      <div className="w-16 h-16 bg-primary-glow rounded-full flex items-center justify-center">
                        <ShoppingBag className="w-8 h-8 text-white" />
                      </div>
                    </div>
                  )}
                </div>

                <CardContent className="p-6">
                  <div className="flex items-start justify-between mb-3">
                    <h3 className="font-bold text-lg text-white mb-2">
                      {item.name}
                    </h3>
                    <span className="text-2xl font-bold text-primary-glow">
                      ${item.price}
                    </span>
                  </div>

                  <p className="text-white/80 text-sm mb-4 line-clamp-2">
                    {item.desc}
                  </p>

                  <div className="mb-4">
                    <p className="text-white/70 text-sm mb-2">
                      <strong className="text-primary-glow">
                        Why we recommend this:
                      </strong>
                    </p>
                    <p className="text-white/80 text-sm italic">{reason}</p>
                  </div>

                  <div className="flex flex-wrap gap-1 mb-4">
                    {item.sizes_available.slice(0, 5).map((size) => (
                      <Badge
                        key={size}
                        variant="outline"
                        className="text-xs border-white/30 text-white/70"
                      >
                        {size}
                      </Badge>
                    ))}
                    {item.sizes_available.length > 5 && (
                      <Badge
                        variant="outline"
                        className="text-xs border-white/30 text-white/70"
                      >
                        +{item.sizes_available.length - 5} more
                      </Badge>
                    )}
                  </div>

                  <Button
                    variant={isSelected ? "hero" : "glass"}
                    className="w-full"
                    onClick={(e) => {
                      e.stopPropagation();
                      toggleItemSelection(item.name);
                    }}
                  >
                    {isSelected ? "Added to Selection" : "Add to Selection"}
                  </Button>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Selected Items Summary & Continue Button */}
        {selectedItems.size > 0 && (
          <Card className="bg-white/10 backdrop-blur-md border-white/20 text-white sticky bottom-4">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-semibold text-lg mb-1">
                    Ready to Continue
                  </h3>
                  <p className="text-white/80">
                    {selectedItems.size} item{selectedItems.size > 1 ? "s" : ""}{" "}
                    selected
                  </p>
                </div>
                <Button
                  variant="hero"
                  size="lg"
                  onClick={proceedToFinal}
                  className="flex items-center gap-2"
                >
                  Continue to Final Step
                  <ArrowRight className="w-5 h-5" />
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {filteredRecommendations.length === 0 && !loading && (
          <Card className="bg-white/10 backdrop-blur-md border-white/20 text-white">
            <CardContent className="p-8 text-center">
              <ShoppingBag className="w-16 h-16 mx-auto mb-4 text-white/50" />
              <h3 className="text-xl font-semibold mb-2">No items found</h3>
              <p className="text-white/80 mb-4">
                No clothing items match your current filter, or there was an
                issue loading recommendations.
              </p>
              <div className="flex gap-4 justify-center">
                <Button
                  variant="glass"
                  onClick={() => setSelectedCategory("all")}
                >
                  Show All Items
                </Button>
                <Button
                  variant="hero"
                  onClick={retryFetchRecommendations}
                  disabled={isRetrying}
                  className="flex items-center gap-2"
                >
                  {isRetrying ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : null}
                  Retry Loading
                </Button>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};

export default PickClothes;
