# Vellum Style Service Module

A Python module for integrating with Vellum AI's "the-big-style" workflow to generate personalized style recommendations based on user preferences and available catalogue items.

## Features

- **Type-safe data structures** for user profiles and catalogue items
- **Flexible API** with both class-based and functional interfaces
- **Comprehensive user profile formatting** matching the expected workflow input format
- **Error handling** with meaningful error messages
- **Example usage** and API integration templates

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your environment variables:
```bash
# In your .env file or environment
VELLUM_API_KEY=your_vellum_api_key_here
```

## Quick Start

### Using the convenience function

```python
from vellum_style_service import get_style_recommendations

# User profile data
user_data = {
    "session_id": "sty_user_001",
    "date": "2025-07-19",
    "style_words": ["clean", "versatile", "modern"],
    "style_message": "I want to look put-together and approachable",
    # ... other profile fields
}

# Catalogue items
catalogue_data = [
    {
        "name": "Slate Supima Crew Tee",
        "desc": "Lightweight premium cotton crewneck...",
        "price": 32,
        "sizes_available": ["XS", "S", "M", "L", "XL"]
    },
    # ... other items
]

# Get recommendations
recommendations = get_style_recommendations(user_data, catalogue_data)
print(recommendations)
```

### Using the service class

```python
from vellum_style_service import VellumStyleService

# Initialize service
service = VellumStyleService()

# Create structured objects
user_profile = service.create_user_profile_from_dict(user_data)
catalogue_items = service.create_catalogue_items_from_list(catalogue_data)

# Execute workflow
result = service.execute_style_workflow(user_profile, catalogue_items)
```

## Data Structures

### UserStyleProfile

The user profile includes:
- **Personal info**: session_id, date
- **Style preferences**: style_words, style_message, style_inspiration
- **Needs & constraints**: daily_needs, occasion, avoid_styles, budget_range
- **Physical attributes**: sizes, measurements, fit_preferences, appearance
- **Context**: location, weather information

### CatalogueItem

Each catalogue item includes:
- **name**: Item name
- **desc**: Item description
- **price**: Price in your currency unit
- **sizes_available**: List of available sizes

## API Integration

The module includes a Flask-based API example (`api_module.py`) that provides:

- `POST /style-recommendations`: Get style recommendations
- `POST /format-user-content`: Format user data for debugging
- `GET /health`: Health check endpoint

### Running the API

```bash
python api_module.py
```

The API will run on `http://localhost:5000`

### Example API request

```bash
curl -X POST http://localhost:5000/style-recommendations \
  -H "Content-Type: application/json" \
  -d '{
    "user_profile": {
      "session_id": "sty_user_001",
      "style_words": ["clean", "modern"],
      "style_message": "I want to look professional"
    },
    "catalogue": [
      {
        "name": "Test Item",
        "desc": "A test item",
        "price": 50,
        "sizes_available": ["M", "L"]
      }
    ]
  }'
```

## Configuration

### Environment Variables

- `VELLUM_API_KEY`: Your Vellum AI API key (required)

### Custom Configuration

You can also pass the API key directly:

```python
service = VellumStyleService(api_key="your_custom_key")
```

## Error Handling

The module includes comprehensive error handling:

- Missing API key validation
- Workflow execution error checking
- Data structure validation
- Network error handling

## Files Overview

- `vellum_style_service.py`: Main module with service class and data structures
- `example_usage.py`: Usage examples
- `api_module.py`: Flask API integration example
- `requirements.txt`: Python dependencies
- `README.md`: This documentation

## Example User Profile Format

The module formats user data into this structure for the Vellum workflow:

```
### Ted's Style Session

**Session ID:** sty_ted_001
**Date:** 2025-07-19

---

### User Preferences

**Style Words:** clean • versatile • modern
**Style Message:** I want to look put-together and approachable
**Style Inspiration:** Neil Patrick Harris casual suits; Scandinavian minimalism
...

### User Attributes

**Standard Sizes:** top M | bottom 32×32 | shoe US 11
**Body Measurements (cm):** chest 102 | waist 84 | hip 100 | inseam 81
...

### Location & Weather Context

**Location:** Toronto, CA
**Weather Snapshot:** 26 °C, partly sunny, humidity 55%, wind 12 kph
**Weather Tags:** warm • dry • breezy
```

## Contributing

When extending this module:
1. Maintain type safety with dataclasses
2. Add comprehensive error handling
3. Update the README with new features
4. Add examples for new functionality

## License

[Add your license information here]
