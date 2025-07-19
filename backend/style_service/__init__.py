"""
Style Service Module

This module provides style recommendation services using Vellum AI.
"""

try:
    from .vellum_style_service import (
        VellumStyleService, 
        UserStyleProfile, 
        CatalogueItem, 
        get_style_recommendations
    )
    __all__ = ['VellumStyleService', 'UserStyleProfile', 'CatalogueItem', 'get_style_recommendations']
except ImportError as e:
    print(f"Warning: Could not import style service components: {e}")
    __all__ = []