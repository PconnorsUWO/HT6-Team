import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
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

interface ClothingItem {
  category: string;
  desc: string;
  image_url: string;
  name: string;
  price: number;
  sizes_available: string[];
}

interface RecommendationItem {
  item: ClothingItem;
  reason: string;
  score: number;
}

interface RecommendationsData {
  top_10: RecommendationItem[];
}

const PickClothes: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [recommendations, setRecommendations] = useState<RecommendationItem[]>(
    []
  );
  const [selectedCategory, setSelectedCategory] = useState<string>("all");
  const [selectedItems, setSelectedItems] = useState<Set<string>>(new Set());

  useEffect(() => {
    fetchRecommendations();
  }, []);

  const fetchRecommendations = async () => {
    try {
      setLoading(true);

      // Simulate API call with dummy data for now
      await new Promise((resolve) => setTimeout(resolve, 2000));

      // Dummy data matching the user's provided structure
      const dummyData: RecommendationsData = {
        top_10: [
          {
            item: {
              category: "shirts",
              desc: "Moisture-wicking micro-knit V-neck that resists clinging in warm commutes.",
              image_url:
                "https://picsum.photos/seed/cooling-tech-vneck-charcoal/600/800",
              name: "Cooling Tech V-Neck (Charcoal)",
              price: 32,
              sizes_available: ["XS", "S", "M", "L", "XL"],
            },
            reason:
              "The charcoal color, v-neck style, and moisture-wicking fabric suit Ted's preferences and the warm weather; the price is well within his budget.",
            score: 95,
          },
          {
            item: {
              category: "shirts",
              desc: "Classic breathable piqué with updated sleeve length for modern proportion.",
              image_url:
                "https://picsum.photos/seed/organic-pique-navy/600/800",
              name: "Organic Piqué Polo (Navy)",
              price: 58,
              sizes_available: ["S", "M", "L", "XL", "XXL"],
            },
            reason:
              "The navy polo fits Ted's preference for versatile, modern styles and his dominant wardrobe colors.  Its breathable piqué fabric is suitable for Toronto's warm weather and his active lifestyle, and the price aligns with his budget.",
            score: 95,
          },
          {
            item: {
              category: "shirts",
              desc: "Silky pima yarns and breathable knit geometry for high heat commutes.",
              image_url:
                "https://picsum.photos/seed/cooling-pima-deepnavy/600/800",
              name: "Cooling Pima Tee (Deep Navy)",
              price: 34,
              sizes_available: ["XS", "S", "M", "L", "XL"],
            },
            reason:
              "The deep navy color, breathable material, and reasonable price align well with Ted's preferences and the warm weather.  The style is versatile enough for his various needs.",
            score: 95,
          },
          {
            item: {
              category: "pants",
              desc: "Polished stretch chino with crease recovery and subtle sateen hand.",
              image_url:
                "https://picsum.photos/seed/performance-dress-chino-navy/600/800",
              name: "Performance Dress Chino (Navy)",
              price: 86,
              sizes_available: [
                "30x30",
                "30x32",
                "32x32",
                "34x32",
                "36x32",
                "38x32",
              ],
            },
            reason:
              "The navy chinos are versatile, fitting Ted's hybrid work style and networking event.  The stretch fabric and tailored fit align with his preferences, and the price is within his budget.",
            score: 95,
          },
          {
            item: {
              category: "pants",
              desc: "Streamlined utility details on a tapered 6-pocket stretch silhouette.",
              image_url:
                "https://picsum.photos/seed/minimal-utility-olive/600/800",
              name: "Minimal Utility Pant (Olive Drab)",
              price: 92,
              sizes_available: ["30x30", "30x32", "32x30", "32x32", "34x32"],
            },
            reason:
              "The olive drab color, tailored fit, and stretch fabric align well with Ted's preferences and the warm weather; the price fits his budget, and a 32x32 is available.",
            score: 95,
          },
        ],
      };

      setRecommendations(dummyData.top_10);
      toast.success("Style recommendations loaded successfully!");
    } catch (error) {
      console.error("Failed to fetch recommendations:", error);
      toast.error("Failed to load recommendations. Please try again.");
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

    toast.success(`Selected ${selectedItems.size} items for your wardrobe!`);
    navigate("/final");
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
                best clothing recommendations just for you...
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

          <Badge
            variant="secondary"
            className="bg-primary/20 text-primary-glow border-primary-glow/30"
          >
            {recommendations.length} items found
          </Badge>
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

        {filteredRecommendations.length === 0 && (
          <Card className="bg-white/10 backdrop-blur-md border-white/20 text-white">
            <CardContent className="p-8 text-center">
              <ShoppingBag className="w-16 h-16 mx-auto mb-4 text-white/50" />
              <h3 className="text-xl font-semibold mb-2">No items found</h3>
              <p className="text-white/80 mb-4">
                No clothing items match your current filter. Try selecting a
                different category.
              </p>
              <Button
                variant="glass"
                onClick={() => setSelectedCategory("all")}
              >
                Show All Items
              </Button>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};

export default PickClothes;
