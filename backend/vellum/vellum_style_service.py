"""
Vellum AI Style Service Module

This module provides an interface to the Vellum AI "the-big-style" workflow
for generating personalized style recommendations based on user preferences
and available catalogue items.
"""

import os
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from vellum.client import Vellum
import vellum.types as types


@dataclass
class UserStyleProfile:
    """User style profile data structure"""
    session_id: str
    date: str
    style_words: List[str]
    style_message: str
    style_inspiration: str
    daily_needs: List[str]
    occasion: str
    avoid_styles: List[str]
    avoid_materials: List[str]
    material_sensitivities: List[str]
    dominant_colors: List[str]
    accessory_preferences: List[str]
    budget_range: str
    notes: str
    standard_sizes: Dict[str, str]
    body_measurements: Dict[str, int]
    fit_preferences: List[str]
    skin_tone: str
    hair: str
    eyes: str
    location: str
    weather_snapshot: str
    weather_tags: List[str]


@dataclass
class CatalogueItem:
    """Catalogue item data structure"""
    name: str
    desc: str
    price: int
    sizes_available: List[str]


class VellumStyleService:
    """Service class for interacting with Vellum AI style workflow"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Vellum Style Service
        
        Args:
            api_key: Vellum API key. If not provided, will use VELLUM_API_KEY env var
        """
        self.api_key = api_key or os.environ.get("VELLUM_API_KEY")
        if not self.api_key:
            raise ValueError("VELLUM_API_KEY must be provided or set in environment variables")
        
        self.client = Vellum(api_key=self.api_key)
        self.workflow_name = "the-big-style"
    
    def format_user_content(self, profile: UserStyleProfile) -> str:
        """
        Format user profile data into the content string expected by the workflow
        
        Args:
            profile: UserStyleProfile object containing all user data
            
        Returns:
            Formatted content string
        """
        content = f"""### {profile.session_id.replace('_', ' ').title()}'s Style Session

**Session ID:** {profile.session_id}
**Date:** {profile.date}

---

### User Preferences

**Style Words:** {' • '.join(profile.style_words)}
**Style Message:** {profile.style_message}
**Style Inspiration:** {profile.style_inspiration}
**Daily Needs:** {' • '.join(profile.daily_needs)}
**Occasion:** {profile.occasion}
**Avoid (Styles / Items):** {' • '.join(profile.avoid_styles)}
**Avoid (Materials):** {' • '.join(profile.avoid_materials)}
**Material Sensitivities:** {' • '.join(profile.material_sensitivities)}
**Dominant Wardrobe Colors:** {' • '.join(profile.dominant_colors)}
**Accessory Preferences:** {' • '.join(profile.accessory_preferences)}
**Budget (Per Item):** {profile.budget_range}
**Notes:** {profile.notes}

---

### User Attributes

**Standard Sizes:** {' | '.join([f"{k} {v}" for k, v in profile.standard_sizes.items()])}
**Body Measurements (cm):** {' | '.join([f"{k} {v}" for k, v in profile.body_measurements.items()])}
**Fit Preferences:** {' • '.join(profile.fit_preferences)}
**Skin Tone / Undertone:** {profile.skin_tone}
**Hair:** {profile.hair}
**Eyes:** {profile.eyes}

---

### Location & Weather Context

**Location:** {profile.location}
**Weather Snapshot:** {profile.weather_snapshot}
**Weather Tags:** {' • '.join(profile.weather_tags)}"""
        
        return content
    
    def execute_style_workflow(
        self, 
        user_profile: UserStyleProfile, 
        catalogue_items: List[CatalogueItem],
        release_tag: str = "LATEST"
    ) -> Dict[str, Any]:
        """
        Execute the Vellum style workflow with user profile and catalogue data
        
        Args:
            user_profile: UserStyleProfile object with user data
            catalogue_items: List of CatalogueItem objects
            release_tag: Workflow release tag (default: "LATEST")
            
        Returns:
            Dictionary containing the workflow output
            
        Raises:
            Exception: If workflow execution fails
        """
        # Format user content
        content = self.format_user_content(user_profile)
        
        # Convert catalogue items to the expected format
        catalogue_data = [
            {
                "name": item.name,
                "desc": item.desc,
                "price": item.price,
                "sizes_available": item.sizes_available
            }
            for item in catalogue_items
        ]
        
        try:
            # Execute the workflow
            result = self.client.execute_workflow(
                workflow_deployment_name=self.workflow_name,
                release_tag=release_tag,
                inputs=[
                    types.WorkflowRequestStringInputRequest(
                        name="content",
                        type="STRING",
                        value=content,
                    ),
                    types.WorkflowRequestJsonInputRequest(
                        name="catalogue_available",
                        type="JSON",
                        value=catalogue_data,
                    ),
                ],
            )
            
            # Check for errors
            if result.data.state == "REJECTED":
                raise Exception(f"Workflow execution failed: {result.data.error.message}")
            
            return result.data.outputs
            
        except Exception as e:
            raise Exception(f"Failed to execute style workflow: {str(e)}")
    
    def create_user_profile_from_dict(self, data: Dict[str, Any]) -> UserStyleProfile:
        """
        Create a UserStyleProfile from a dictionary
        
        Args:
            data: Dictionary containing user profile data
            
        Returns:
            UserStyleProfile object
        """
        return UserStyleProfile(
            session_id=data.get('session_id', ''),
            date=data.get('date', datetime.now().strftime('%Y-%m-%d')),
            style_words=data.get('style_words', []),
            style_message=data.get('style_message', ''),
            style_inspiration=data.get('style_inspiration', ''),
            daily_needs=data.get('daily_needs', []),
            occasion=data.get('occasion', ''),
            avoid_styles=data.get('avoid_styles', []),
            avoid_materials=data.get('avoid_materials', []),
            material_sensitivities=data.get('material_sensitivities', []),
            dominant_colors=data.get('dominant_colors', []),
            accessory_preferences=data.get('accessory_preferences', []),
            budget_range=data.get('budget_range', ''),
            notes=data.get('notes', ''),
            standard_sizes=data.get('standard_sizes', {}),
            body_measurements=data.get('body_measurements', {}),
            fit_preferences=data.get('fit_preferences', []),
            skin_tone=data.get('skin_tone', ''),
            hair=data.get('hair', ''),
            eyes=data.get('eyes', ''),
            location=data.get('location', ''),
            weather_snapshot=data.get('weather_snapshot', ''),
            weather_tags=data.get('weather_tags', [])
        )
    
    def create_catalogue_items_from_list(self, items: List[Dict[str, Any]]) -> List[CatalogueItem]:
        """
        Create a list of CatalogueItem objects from a list of dictionaries
        
        Args:
            items: List of dictionaries containing catalogue item data
            
        Returns:
            List of CatalogueItem objects
        """
        return [
            CatalogueItem(
                name=item.get('name', ''),
                desc=item.get('desc', ''),
                price=item.get('price', 0),
                sizes_available=item.get('sizes_available', [])
            )
            for item in items
        ]


# Convenience function for quick usage
def get_style_recommendations(
    user_data: Dict[str, Any], 
    catalogue_data: List[Dict[str, Any]],
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Convenience function to get style recommendations
    
    Args:
        user_data: Dictionary containing user profile data
        catalogue_data: List of dictionaries containing catalogue items
        api_key: Optional Vellum API key
        
    Returns:
        Dictionary containing style recommendations
    """
    service = VellumStyleService(api_key)
    user_profile = service.create_user_profile_from_dict(user_data)
    catalogue_items = service.create_catalogue_items_from_list(catalogue_data)
    
    return service.execute_style_workflow(user_profile, catalogue_items)
