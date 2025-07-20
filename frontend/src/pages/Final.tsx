import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { ArrowLeft, ChevronLeft, ChevronRight, Sparkles, Home } from "lucide-react";
import { useNavigate } from "react-router-dom";

const Final = () => {
  const navigate = useNavigate();
  const [currentCategory, setCurrentCategory] = useState("shirt");
  const [recommendationIndex, setRecommendationIndex] = useState(0);

  const recommendations = [
    {
      title: "Classic Sophistication",
      description: "Try pairing this classic white button-down with dark chinos for a sophisticated casual look. The clean lines complement your features perfectly.",
      image: "/lovable-uploads/47ddf8ec-e767-4383-ba70-1d2b84565232.png",
      tags: ["Casual", "Professional", "Versatile"]
    },
    {
      title: "Modern Edge",
      description: "A relaxed v-neck tee in soft cotton creates an effortless, approachable style. Perfect for weekend outings or casual meetings.",
      image: "/lovable-uploads/47ddf8ec-e767-4383-ba70-1d2b84565232.png",
      tags: ["Relaxed", "Weekend", "Comfortable"]
    },
    {
      title: "Smart Casual",
      description: "Elevate your look with a well-fitted polo shirt. This timeless piece bridges the gap between casual and formal beautifully.",
      image: "/lovable-uploads/47ddf8ec-e767-4383-ba70-1d2b84565232.png",
      tags: ["Smart Casual", "Timeless", "Versatile"]
    }
  ];

  const categories = [
    { id: "shirt", label: "Shirts", icon: "👕" },
    { id: "pants", label: "Pants", icon: "👖" },
    { id: "dresses", label: "Dresses", icon: "👗" },
    { id: "accessories", label: "Accessories", icon: "👜" }
  ];

  const alternativeItems = {
    shirt: [
      { name: "Linen Shirt", color: "White", price: "$89", match: "95%" },
      { name: "Cotton Polo", color: "Navy", price: "$65", match: "88%" },
      { name: "Oxford Button-down", color: "Light Blue", price: "$95", match: "92%" }
    ],
    pants: [
      { name: "Slim Chinos", color: "Khaki", price: "$75", match: "90%" },
      { name: "Dress Pants", color: "Charcoal", price: "$120", match: "87%" },
      { name: "Dark Jeans", color: "Indigo", price: "$95", match: "85%" }
    ],
    dresses: [
      { name: "Midi Dress", color: "Black", price: "$140", match: "93%" },
      { name: "Wrap Dress", color: "Navy", price: "$110", match: "89%" },
      { name: "Shirt Dress", color: "White", price: "$95", match: "91%" }
    ],
    accessories: [
      { name: "Leather Belt", color: "Brown", price: "$45", match: "96%" },
      { name: "Canvas Bag", color: "Tan", price: "$85", match: "88%" },
      { name: "Watch", color: "Silver", price: "$220", match: "94%" }
    ]
  };

  const currentRecommendation = recommendations[recommendationIndex];
  const currentAlternatives = alternativeItems[currentCategory as keyof typeof alternativeItems];

  const nextRecommendation = () => {
    setRecommendationIndex((prev) => (prev + 1) % recommendations.length);
  };

  const prevRecommendation = () => {
    setRecommendationIndex((prev) => (prev - 1 + recommendations.length) % recommendations.length);
  };

  return (
    <div className="min-h-screen bg-gradient-background relative overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute inset-0 opacity-20">
        <div className="absolute top-20 left-10 w-72 h-72 bg-primary-glow/30 rounded-full blur-3xl animate-float"></div>
        <div className="absolute bottom-20 right-10 w-96 h-96 bg-primary/20 rounded-full blur-3xl animate-float" style={{animationDelay: '1.5s'}}></div>
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
            <h1 className="text-xl font-semibold">Style Journey</h1>
          </div>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
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
                  <span>{recommendationIndex + 1} of {recommendations.length}</span>
                  <span>AI Styled</span>
                </div>
              </div>
            </Card>

            {/* Style Confidence */}
            <Card className="p-4 bg-white/10 backdrop-blur-md border-white/20 text-white animate-scale-in" style={{animationDelay: '0.2s'}}>
              <h4 className="font-medium mb-3 text-sm flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-primary-glow" />
                Style Confidence
              </h4>
              <div className="flex items-center gap-3">
                <div className="flex-1 bg-white/10 rounded-full h-3">
                  <div className="bg-gradient-primary h-3 rounded-full w-4/5 animate-pulse"></div>
                </div>
                <span className="text-sm font-semibold">92%</span>
              </div>
              <p className="text-xs text-white/70 mt-2">
                This style matches your preferences perfectly
              </p>
            </Card>
          </div>

          {/* Center - Main Image */}
          <div className="flex items-center justify-center animate-scale-in" style={{animationDelay: '0.3s'}}>
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-primary rounded-2xl blur-xl opacity-30 scale-110"></div>
              <Card className="relative overflow-hidden bg-white/5 backdrop-blur-sm border-white/20 p-2">
                <img
                  src={currentRecommendation.image}
                  alt="Style recommendation"
                  className="w-full max-w-sm h-96 object-cover rounded-xl"
                />
                <div className="absolute top-4 left-4">
                  <span className="px-3 py-1 bg-black/50 backdrop-blur-sm text-white text-xs rounded-full">
                    Recommended Look
                  </span>
                </div>
              </Card>
            </div>
          </div>

          {/* Right Panel - Alternative Items */}
          <div className="space-y-4 animate-slide-in-right" style={{animationDelay: '0.4s'}}>
            <div className="text-white mb-4">
              <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
                <ArrowLeft className="w-4 h-4" />
                Alternative {categories.find(c => c.id === currentCategory)?.label}
              </h3>
            </div>

            <div className="space-y-3">
              {currentAlternatives.map((item, index) => (
                <Card
                  key={index}
                  className="p-4 bg-white/10 backdrop-blur-md border-white/20 text-white hover:bg-white/15 transition-all duration-300 cursor-pointer group hover:scale-105"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <p className="font-medium text-sm">{item.name}</p>
                      <p className="text-xs text-white/70">{item.color}</p>
                    </div>
                    <div className="text-right">
                      <p className="font-semibold text-sm">{item.price}</p>
                      <p className="text-xs text-primary-glow">{item.match} match</p>
                    </div>
                    <ChevronRight className="w-4 h-4 ml-2 opacity-0 group-hover:opacity-100 transition-opacity" />
                  </div>
                </Card>
              ))}
            </div>

            <Button variant="glass" className="w-full mt-6">
              View More Options
            </Button>
          </div>
        </div>

        {/* Category Navigation - Bottom */}
        <div className="mt-12 animate-slide-in-right" style={{animationDelay: '0.5s'}}>
          <div className="flex justify-center">
            <div className="grid grid-cols-4 gap-4 max-w-md">
              {categories.map((category) => (
                <Button
                  key={category.id}
                  variant={currentCategory === category.id ? "glass" : "category"}
                  onClick={() => setCurrentCategory(category.id)}
                  className="h-20 flex-col gap-2 text-white"
                >
                  <span className="text-2xl">{category.icon}</span>
                  <span className="text-xs">{category.label}</span>
                </Button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Final;