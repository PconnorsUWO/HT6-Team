// User profile interface
export interface UserProfile {
  session_id: string;
  date: string;
  style_words: string[];
  style_message: string;
  style_inspiration: string;
  daily_needs: string[];
  occasion: string;
  avoid_styles: string[];
  avoid_materials: string[];
  material_sensitivities: string[];
  dominant_colors: string[];
  accessory_preferences: string[];
  budget_range: string;
  notes: string;
  standard_sizes: {
    top: string;
    bottom: string;
    shoe: string;
  };
  body_measurements: {
    chest: number;
    waist: number;
    hip: number;
    inseam: number;
  };
  fit_preferences: string[];
  skin_tone: string;
  hair: string;
  eyes: string;
  location: string;
  weather_snapshot: string;
  weather_tags: string[];
}

// Example user profile based on Ted's data
export const tedProfileData: UserProfile = {
  session_id: "sty_ted_001",
  date: "2025-07-19",
  style_words: ["clean", "versatile", "modern"],
  style_message: "I want to look put-together and approachable without seeming overdressed.",
  style_inspiration: "Neil Patrick Harris casual suits; Scandinavian minimalism",
  daily_needs: ["hybrid office", "casual remote days", "evening meetup events", "weekend brunches"],
  occasion: "networking mixer",
  avoid_styles: ["neon", "extra baggy fits", "loud logos", "heavy distressed denim"],
  avoid_materials: ["polyester"],
  material_sensitivities: ["wool"],
  dominant_colors: ["navy", "charcoal", "white", "olive"],
  accessory_preferences: ["minimal watch", "leather belt"],
  budget_range: "$50–$180",
  notes: "Commutes by bike; prefers breathable stretch fabrics.",
  standard_sizes: {
    top: "M",
    bottom: "32×32",
    shoe: "US 11"
  },
  body_measurements: {
    chest: 102,
    waist: 84,
    hip: 100,
    inseam: 81
  },
  fit_preferences: ["tailored", "regular"],
  skin_tone: "light / cool",
  hair: "light brown, short textured",
  eyes: "blue",
  location: "Toronto, CA",
  weather_snapshot: "26 °C, partly sunny, humidity 55%, wind 12 kph",
  weather_tags: ["warm", "dry", "breezy"]
};