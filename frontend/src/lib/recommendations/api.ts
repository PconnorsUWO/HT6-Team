import { UserProfile } from "./const/userprofile";
import { RecommendationsContext } from "./const/catalogue";

// Base URL for the recommendations API
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:5000";
const RECOMMENDATIONS_BASE = `${API_BASE_URL}/api/recommendations`;

// Types for API responses
export interface CatalogueItem {
  name: string;
  desc: string;
  price: number;
  category: string;
  image_url: string;
  sizes_available: string[];
}

export interface RecommendationItem {
  item: CatalogueItem;
  reason: string;
  score: number;
}

export interface StyleRecommendationsResponse {
  success: boolean;
  user_session_id: string;
  recommendations: {
    "final-output"?: {
      top_10: RecommendationItem[];
    };
    top_10?: RecommendationItem[];
  };
  catalogue_count: number;
  message: string;
}

export interface QuickRecommendationsResponse {
  success: boolean;
  recommendations: {
    "final-output"?: {
      top_10: RecommendationItem[];
    };
    top_10?: RecommendationItem[];
  };
  message: string;
}

export interface ProfileValidationResponse {
  success: boolean;
  is_valid: boolean;
  errors?: string[];
  completeness_percentage?: number;
  message: string;
}

export interface ProfileTemplateResponse {
  success: boolean;
  template: UserProfile;
  description: string;
}

export interface CatalogueTemplateResponse {
  success: boolean;
  template: CatalogueItem[];
  description: string;
}

export interface StylePreferencesResponse {
  success: boolean;
  preferences: {
    style_words: string[];
    occasions: string[];
    budget_ranges: string[];
    fit_preferences: string[];
    colors: string[];
    materials_to_avoid: string[];
  };
  description: string;
}

export interface QuickRecommendationRequest {
  session_id: string;
  style_words: string[];
  occasion: string;
  budget_range: string;
  dominant_colors?: string[];
  fit_preferences?: string[];
  avoid_styles?: string[];
  location?: string;
  catalogue_items?: CatalogueItem[];
}

export interface ApiError {
  success: false;
  error: string;
  details?: string;
}

// Helper function to handle API errors
const handleApiError = async (response: Response): Promise<never> => {
  const errorData = await response.json().catch(() => ({
    error: "Failed to parse error response",
  }));

  throw {
    success: false,
    error: errorData.error || `HTTP ${response.status}: ${response.statusText}`,
    details: errorData.details || errorData.message,
  } as ApiError;
};

// Helper function to make API requests
const apiRequest = async <T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> => {
  const url = `${RECOMMENDATIONS_BASE}${endpoint}`;

  const defaultOptions: RequestInit = {
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  };

  const response = await fetch(url, { ...defaultOptions, ...options });

  if (!response.ok) {
    await handleApiError(response);
  }

  return response.json();
};

/**
 * Get personalized style recommendations based on user profile
 * Automatically uses the full catalogue for recommendations
 */
export const getStyleRecommendations = async (
  userProfile: UserProfile,
  catalogueItems?: CatalogueItem[]
): Promise<StyleRecommendationsResponse> => {
  // Use provided catalogue items or default to the full catalogue
  const itemsToUse =
    catalogueItems || formatCatalogueItems(RecommendationsContext);

  return apiRequest<StyleRecommendationsResponse>("/style-recommendations", {
    method: "POST",
    body: JSON.stringify({
      user_profile: userProfile,
      catalogue_items: itemsToUse,
    }),
  });
};

/**
 * Get quick style recommendations with simplified input
 * Automatically includes the full catalogue for recommendations
 */
export const getQuickRecommendations = async (
  request: QuickRecommendationRequest
): Promise<QuickRecommendationsResponse> => {
  // Add the full catalogue to the request
  const requestWithCatalogue = {
    ...request,
    catalogue_items: formatCatalogueItems(RecommendationsContext),
  };

  return apiRequest<QuickRecommendationsResponse>("/quick-recommendations", {
    method: "POST",
    body: JSON.stringify(requestWithCatalogue),
  });
};

/**
 * Validate user profile data before generating recommendations
 */
export const validateUserProfile = async (
  userProfile: Partial<UserProfile>
): Promise<ProfileValidationResponse> => {
  return apiRequest<ProfileValidationResponse>("/validate-profile", {
    method: "POST",
    body: JSON.stringify({ user_profile: userProfile }),
  });
};

/**
 * Get a template for user profile data structure
 */
export const getProfileTemplate =
  async (): Promise<ProfileTemplateResponse> => {
    return apiRequest<ProfileTemplateResponse>("/profile-template", {
      method: "GET",
    });
  };

/**
 * Get a template for catalogue item data structure
 */
export const getCatalogueTemplate =
  async (): Promise<CatalogueTemplateResponse> => {
    return apiRequest<CatalogueTemplateResponse>("/catalogue-template", {
      method: "GET",
    });
  };

/**
 * Get available style preference options
 */
export const getStylePreferences =
  async (): Promise<StylePreferencesResponse> => {
    return apiRequest<StylePreferencesResponse>("/style-preferences", {
      method: "GET",
    });
  };

// Helper functions for working with recommendations

/**
 * Calculate the completeness percentage of a user profile
 */
export const calculateProfileCompleteness = (
  profile: Partial<UserProfile>
): number => {
  const requiredFields = [
    "session_id",
    "style_words",
    "style_message",
    "occasion",
    "budget_range",
    "dominant_colors",
    "fit_preferences",
    "skin_tone",
    "location",
  ];

  const completedFields = requiredFields.filter((field) => {
    const value = profile[field as keyof UserProfile];
    return (
      value !== undefined &&
      value !== null &&
      value !== "" &&
      (Array.isArray(value) ? value.length > 0 : true)
    );
  });

  return Math.round((completedFields.length / requiredFields.length) * 100);
};

/**
 * Create a quick recommendation request from a partial user profile
 */
export const createQuickRecommendationRequest = (
  profile: Partial<UserProfile>
): QuickRecommendationRequest => {
  if (
    !profile.session_id ||
    !profile.style_words ||
    !profile.occasion ||
    !profile.budget_range
  ) {
    throw new Error(
      "Missing required fields for quick recommendations: session_id, style_words, occasion, budget_range"
    );
  }

  return {
    session_id: profile.session_id,
    style_words: profile.style_words,
    occasion: profile.occasion,
    budget_range: profile.budget_range,
    dominant_colors: profile.dominant_colors,
    fit_preferences: profile.fit_preferences,
    avoid_styles: profile.avoid_styles,
    location: profile.location,
  };
};

/**
 * Format user profile for API consumption (removes undefined/null values)
 */
export const formatUserProfileForApi = (
  profile: Partial<UserProfile>
): Partial<UserProfile> => {
  const formatted: Partial<UserProfile> = {};

  Object.entries(profile).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      // For arrays, only include if not empty
      if (Array.isArray(value) && value.length === 0) {
        return;
      }
      // For strings, only include if not empty
      if (typeof value === "string" && value.trim() === "") {
        return;
      }
      (formatted as Record<string, unknown>)[key] = value;
    }
  });

  return formatted;
};

/**
 * Merge catalogue items with default fields
 */
export const formatCatalogueItems = (
  items: Partial<CatalogueItem>[]
): CatalogueItem[] => {
  return items.map((item) => ({
    name: item.name || "Unknown Item",
    desc: item.desc || "No description available",
    price: item.price || 0,
    sizes_available: item.sizes_available || [],
    category: item.category,
    image_url: item.image_url,
  }));
};

// Error handling utilities
export const isApiError = (error: unknown): error is ApiError => {
  return (
    typeof error === "object" &&
    error !== null &&
    "success" in error &&
    "error" in error
  );
};

export const getErrorMessage = (error: unknown): string => {
  if (isApiError(error)) {
    return error.details || error.error;
  }
  if (error instanceof Error) {
    return error.message;
  }
  return "An unknown error occurred";
};

// React Query keys for caching
export const recommendationsQueryKeys = {
  all: ["recommendations"] as const,
  styleRecommendations: (userSessionId: string) =>
    [...recommendationsQueryKeys.all, "style", userSessionId] as const,
  quickRecommendations: (sessionId: string) =>
    [...recommendationsQueryKeys.all, "quick", sessionId] as const,
  profileTemplate: () =>
    [...recommendationsQueryKeys.all, "profile-template"] as const,
  catalogueTemplate: () =>
    [...recommendationsQueryKeys.all, "catalogue-template"] as const,
  stylePreferences: () =>
    [...recommendationsQueryKeys.all, "style-preferences"] as const,
};

export default {
  getStyleRecommendations,
  getQuickRecommendations,
  validateUserProfile,
  getProfileTemplate,
  getCatalogueTemplate,
  getStylePreferences,
  calculateProfileCompleteness,
  createQuickRecommendationRequest,
  formatUserProfileForApi,
  formatCatalogueItems,
  isApiError,
  getErrorMessage,
  recommendationsQueryKeys,
};
