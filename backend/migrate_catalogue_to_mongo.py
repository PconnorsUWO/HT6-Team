import os
#!/usr/bin/env python3
"""
Catalogue Migration Script

This script migrates the hardcoded catalogue data from the frontend TypeScript file
to a MongoDB collection. It creates a 'catalogue' collection and populates it with
all the clothing items.

Usage:
    python migrate_catalogue_to_mongo.py [--drop-existing] [--verbose]

Options:
    --drop-existing  Drop the existing catalogue collection before inserting new data
    --verbose        Enable verbose logging
"""

import sys
import argparse
import logging
from datetime import datetime
from typing import List, Dict, Any
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, DuplicateKeyError
from config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Catalogue data converted from TypeScript
CATALOGUE_DATA = [
    {
        "desc": "A chic brown midi dress with a structured fit and a statement belt for a polished look.",
        "name": "Belted Brown Midi Dress",
        "price": 104.99,
        "category": "dresses",
        "image_url": "/catalog/brown_midi_dress.jpg",
        "sizes_available": ["XS", "S", "M", "L", "XL"],
    },
    {
        "desc": "A breezy yellow printed dress with a smocked top, perfect for sunny days.",
        "name": "Yellow Printed Midi Dress",
        "price": 97.5,
        "category": "dresses",
        "image_url": "/catalog/yellow_midi_dress.jpg",
        "sizes_available": ["XS", "S", "M", "L", "XL"],
    },
    {
        "desc": "An off-shoulder floral dress featuring a colorful, artistic print and flowy silhouette.",
        "name": "Floral Off-Shoulder Dress",
        "price": 108.25,
        "category": "dresses",
        "image_url": "/catalog/painted_dress.jpg",
        "sizes_available": ["XS", "S", "M", "L", "XL"],
    },
    {
        "desc": "A sleeveless beige wrap dress with contrasting trim and a textured waist belt for a tailored fit.",
        "name": "Beige Wrap Midi Dress",
        "price": 102.3,
        "category": "dresses",
        "image_url": "/catalog/white_madi_dress.jpg",
        "sizes_available": ["XS", "S", "M", "L", "XL"],
    },
    {
        "desc": "A fitted olive green midi dress with ruching and an elegant shoulder brooch.",
        "name": "Ruched Olive Midi Dress",
        "price": 106.9,
        "category": "dresses",
        "image_url": "/catalog/green_dress.jpg",
        "sizes_available": ["XS", "S", "M", "L", "XL"],
    },
    {
        "desc": "A sleek red satin slip dress with a minimalist silhouette and delicate straps.",
        "name": "Red Satin Slip Dress",
        "price": 99.8,
        "category": "dresses",
        "image_url": "/catalog/red_satin_dress.jpg",
        "sizes_available": ["XS", "S", "M", "L", "XL"],
    },
    {
        "desc": "A deep burgundy dress with draped details and a metallic pin accent on the shoulder.",
        "name": "Burgundy Draped Dress",
        "price": 109.2,
        "category": "dresses",
        "image_url": "/catalog/red_dress.jpg",
        "sizes_available": ["XS", "S", "M", "L", "XL"],
    },
    {
        "desc": "A white midi dress with a structured bodice and wide straps for an elegant summer look.",
        "name": "White Structured Midi Dress",
        "price": 100.6,
        "category": "dresses",
        "image_url": "/catalog/white_maxi_dress.jpg",
        "sizes_available": ["XS", "S", "M", "L", "XL"],
    },
    {
        "desc": "A crisp white button-up jumpsuit with wide legs and a flattering waist belt.",
        "name": "White Belted Jumpsuit",
        "price": 84.75,
        "category": "dresses",
        "image_url": "/catalog/white_jumpsuit.jpg",
        "sizes_available": ["XS", "S", "M", "L", "XL"],
    },
    {
        "desc": "A pair of off-white wide-leg trousers crafted from breathable fabric for all-day comfort.",
        "name": "White Wide-Leg Trousers",
        "price": 92.6,
        "category": "lower_body",
        "image_url": "/catalog/white_wide_pants.jpg",
        "sizes_available": ["XS", "S", "M", "L", "XL"],
    },
    {
        "desc": "A slate blue ruched bodycon dress with a single-shoulder neckline and gold-tone shell embellishment.",
        "name": "One-Shoulder Ruched Dress",
        "price": 107.95,
        "category": "dresses",
        "image_url": "/catalog/seashell_dress.jpg",
        "sizes_available": ["XS", "S", "M", "L", "XL"],
    },
    {
        "desc": "Tailored sage green Bermuda shorts with a suede-effect belt for a refined summer look.",
        "name": "Belted Pleated Shorts",
        "price": 86.4,
        "category": "lower_body",
        "image_url": "/catalog/green_shorts.jpg",
        "sizes_available": ["XS", "S", "M", "L", "XL"],
    },
    {
        "desc": "Knitted drawstring pants in a deep green plaid with a soft, cozy feel and elastic waistband.",
        "name": "Green Knit Plaid Pants",
        "price": 89.5,
        "category": "lower_body",
        "image_url": "/catalog/green_pants.jpg",
        "sizes_available": ["XS", "S", "M", "L", "XL"],
    },
    {
        "desc": "Relaxed-fit tie-dye inspired velour pants in warm red tones, ideal for cozy styling.",
        "name": "Red Swirl Velour Pants",
        "price": 90.8,
        "category": "lower_body",
        "image_url": "/catalog/red_pants.jpg",
        "sizes_available": ["XS", "S", "M", "L", "XL"],
    },
    {
        "desc": "Classic white sweatpants in a breathable cotton blend with adjustable drawstring waist.",
        "name": "White Drawstring Sweatpants",
        "price": 85.99,
        "category": "lower_body",
        "image_url": "/catalog/sweats_white.jpg",
        "sizes_available": ["XS", "S", "M", "L", "XL"],
    },
    {
        "desc": "Minimalist black shorts with an elasticated waist and textured finish for everyday comfort.",
        "name": "Black Textured Knit Shorts",
        "price": 83.45,
        "category": "lower_body",
        "image_url": "/catalog/shorts.jpg",
        "sizes_available": ["XS", "S", "M", "L", "XL"],
    },
    {
        "desc": "Light yellow button-up shirt with a crisp collar and subtle structure, perfect for layering or standalone wear.",
        "name": "Soft Yellow Button-Up Shirt",
        "price": 78.2,
        "category": "upper_body",
        "image_url": "/catalog/yellow_button.jpg",
        "sizes_available": ["XS", "S", "M", "L", "XL"],
    },
    {
        "desc": "Elegant white wide-leg trousers with tailored seams and a clean, minimalist silhouette.",
        "name": "White Tailored Trousers",
        "price": 94.1,
        "category": "lower_body",
        "image_url": "/catalog/white_pants.jpg",
        "sizes_available": ["XS", "S", "M", "L", "XL"],
    },
    {
        "desc": "Classic light-wash jeans with a high waist and relaxed straight-leg cut for casual comfort.",
        "name": "Washed Gray Straight Jeans",
        "price": 91.35,
        "category": "lower_body",
        "image_url": "/catalog/gray_jeans.jpg",
        "sizes_available": ["XS", "S", "M", "L", "XL"],
    },
    {
        "desc": "A bold short-sleeve shirt featuring vertical black and white stripes, perfect for a crisp summer look.",
        "name": "Vertical Stripe Short-Sleeve Shirt",
        "price": 69.5,
        "category": "upper_body",
        "image_url": "/catalog/stripe_shirt.jpg",
        "sizes_available": ["XS", "S", "M", "L", "XL"],
    },
    {
        "desc": "Short-sleeve floral shirt in muted olive tones with a soft, breezy linen blend and chest pocket.",
        "name": "Olive Floral Camp Collar Shirt",
        "price": 74.99,
        "category": "upper_body",
        "image_url": "/catalog/floral_shirt.jpg",
        "sizes_available": ["XS", "S", "M", "L", "XL"],
    },
    {
        "desc": "Classic oversized white tee made from breathable cotton, ideal for layering or solo wear.",
        "name": "Basic White Oversized T-Shirt",
        "price": 65.0,
        "category": "upper_body",
        "image_url": "/catalog/white_shirt.jpg",
        "sizes_available": ["XS", "S", "M", "L", "XL"],
    },
    {
        "desc": "A sleek navy blue knit polo shirt with a clean three-button collar and soft texture.",
        "name": "Navy Knit Polo Shirt",
        "price": 72.3,
        "category": "upper_body",
        "image_url": "/catalog/polo_shirt.jpg",
        "sizes_available": ["XS", "S", "M", "L", "XL"],
    },
    {
        "desc": "Light-wash denim jeans with a relaxed fit and high-rise waist for laid-back everyday wear.",
        "name": "Light Blue Relaxed Jeans",
        "price": 88.25,
        "category": "lower_body",
        "image_url": "/catalog/jeans.jpg",
        "sizes_available": ["XS", "S", "M", "L", "XL"],
    },
    {
        "desc": "A deep navy blue button-up shirt with a structured collar and chest pocket for everyday smart-casual wear.",
        "name": "Dark Navy Cotton Shirt",
        "price": 81.9,
        "category": "upper_body",
        "image_url": "/catalog/button_shirt.jpg",
        "sizes_available": ["XS", "S", "M", "L", "XL"],
    },
    {
        "desc": "Refined beige linen blazer with notched lapels and flap pockets—perfect for summer formal wear.",
        "name": "Beige Linen Blazer",
        "price": 85.0,
        "category": "upper_body",
        "image_url": "/catalog/blazer.jpg",
        "sizes_available": ["XS", "S", "M", "L", "XL"],
    },
    {
        "desc": "Slim-fit black trousers made from breathable fabric for elevated comfort and style.",
        "name": "Black Lightweight Trousers",
        "price": 93.7,
        "category": "lower_body",
        "image_url": "/catalog/black_pants.jpg",
        "sizes_available": ["XS", "S", "M", "L", "XL"],
    },
    {
        "desc": "Short-sleeve button-up shirt in pure white linen with a relaxed drape and summer-ready cut.",
        "name": "White Linen Open-Collar Shirt",
        "price": 80.4,
        "category": "upper_body",
        "image_url": "/catalog/linen_shirt.jpg",
        "sizes_available": ["XS", "S", "M", "L", "XL"],
    },
    {
        "desc": "Tailored-fit pants crafted from breathable beige linen for an airy, elevated summer outfit.",
        "name": "Beige Linen Slim Pants",
        "price": 90.45,
        "category": "lower_body",
        "image_url": "/catalog/linen_pants.jpg",
        "sizes_available": ["XS", "S", "M", "L", "XL"],
    },
    {
        "desc": "A textured short-sleeve shirt featuring a vertical woven pattern in neutral and blue tones, perfect for layering or wearing on its own.",
        "name": "Textured Woven Pattern Shirt",
        "price": 79.9,
        "category": "upper_body",
        "image_url": "/catalog/textured_shirt.jpg",
        "sizes_available": ["XS", "S", "M", "L", "XL"],
    },
]


class CatalogueMigrator:
    """Handles migration of catalogue data to MongoDB"""
    
    def __init__(self, mongodb_uri: str, database_name: str = "virtual_tryon"):
        """
        Initialize the migrator
        
        Args:
            mongodb_uri: MongoDB connection string
            database_name: Name of the database to use
        """
        self.mongodb_uri = os.getenv('MONGODB_URI')
        self.database_name = database_name
        self.client = None
        self.db = None
        self.collection = None
        
    def connect(self) -> bool:
        """
        Connect to MongoDB
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            logger.info(f"Connecting to MongoDB at {self.mongodb_uri}")
            self.client = MongoClient(self.mongodb_uri)
            
            # Test the connection
            self.client.admin.command('ping')
            
            self.db = self.client[self.database_name]
            self.collection = self.db.catalogue
            
            logger.info(f"Successfully connected to database '{self.database_name}'")
            return True
            
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error connecting to MongoDB: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")
    
    def drop_collection(self) -> bool:
        """
        Drop the existing catalogue collection
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if self.collection:
                self.collection.drop()
                logger.info("Dropped existing catalogue collection")
                return True
        except Exception as e:
            logger.error(f"Failed to drop collection: {e}")
            return False
        return False
    
    def create_indexes(self):
        """Create indexes for better query performance"""
        try:
            # Create indexes
            self.collection.create_index("name", unique=True)
            self.collection.create_index("category")
            self.collection.create_index("price")
            self.collection.create_index([("category", 1), ("price", 1)])
            
            logger.info("Created database indexes")
            
        except Exception as e:
            logger.warning(f"Failed to create indexes: {e}")
    
    def prepare_catalogue_items(self) -> List[Dict[str, Any]]:
        """
        Prepare catalogue items with additional metadata
        
        Returns:
            List of catalogue items ready for insertion
        """
        prepared_items = []
        
        for item in CATALOGUE_DATA:
            # Add metadata
            prepared_item = {
                **item,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "active": True,
                "stock_count": 100,  # Default stock
                "sku": f"CAT_{item['name'].replace(' ', '_').upper()}",
            }
            prepared_items.append(prepared_item)
        
        return prepared_items
    
    def insert_catalogue_items(self, items: List[Dict[str, Any]]) -> bool:
        """
        Insert catalogue items into MongoDB
        
        Args:
            items: List of catalogue items to insert
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info(f"Inserting {len(items)} catalogue items...")
            
            result = self.collection.insert_many(items, ordered=False)
            
            logger.info(f"Successfully inserted {len(result.inserted_ids)} items")
            return True
            
        except DuplicateKeyError as e:
            logger.warning(f"Some items already exist (duplicate names): {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to insert catalogue items: {e}")
            return False
    
    def verify_migration(self) -> bool:
        """
        Verify that the migration was successful
        
        Returns:
            bool: True if verification successful, False otherwise
        """
        try:
            total_count = self.collection.count_documents({})
            expected_count = len(CATALOGUE_DATA)
            
            logger.info(f"Verification: {total_count} items in database, expected {expected_count}")
            
            if total_count != expected_count:
                logger.warning(f"Item count mismatch: got {total_count}, expected {expected_count}")
                return False
            
            # Check a few sample items
            sample_item = self.collection.find_one({"name": "Belted Brown Midi Dress"})
            if not sample_item:
                logger.error("Sample item not found in database")
                return False
                
            logger.info("Migration verification successful!")
            return True
            
        except Exception as e:
            logger.error(f"Failed to verify migration: {e}")
            return False
    
    def print_summary(self):
        """Print a summary of the catalogue collection"""
        try:
            total_items = self.collection.count_documents({})
            
            # Get category breakdown
            pipeline = [
                {"$group": {"_id": "$category", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            
            category_counts = list(self.collection.aggregate(pipeline))
            
            print("\n" + "="*50)
            print("CATALOGUE MIGRATION SUMMARY")
            print("="*50)
            print(f"Total items: {total_items}")
            print("\nItems by category:")
            for cat in category_counts:
                print(f"  {cat['_id']}: {cat['count']} items")
            
            # Price range
            price_stats = self.collection.aggregate([
                {"$group": {
                    "_id": None,
                    "min_price": {"$min": "$price"},
                    "max_price": {"$max": "$price"},
                    "avg_price": {"$avg": "$price"}
                }}
            ])
            
            stats = list(price_stats)[0]
            print(f"\nPrice range: ${stats['min_price']:.2f} - ${stats['max_price']:.2f}")
            print(f"Average price: ${stats['avg_price']:.2f}")
            print("="*50)
            
        except Exception as e:
            logger.error(f"Failed to generate summary: {e}")


def main():
    """Main migration function"""
    parser = argparse.ArgumentParser(description="Migrate catalogue data to MongoDB")
    parser.add_argument("--drop-existing", action="store_true", 
                       help="Drop existing catalogue collection before migration")
    parser.add_argument("--verbose", action="store_true", 
                       help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Check MongoDB URI
    mongodb_uri = os.getenv('MONGODB_URI')
    # if not mongodb_uri:
    #     logger.error("MONGODB_URI not found in configuration. Please set it in your .env file.")
    #     sys.exit(1)
    
    # Initialize migrator
    migrator = CatalogueMigrator(mongodb_uri)
    
    try:
        # Connect to MongoDB
        if not migrator.connect():
            logger.error("Failed to connect to MongoDB. Exiting.")
            sys.exit(1)
        
        # Drop existing collection if requested
        if args.drop_existing:
            logger.info("Dropping existing catalogue collection...")
            migrator.drop_collection()
        
        # Create indexes
        migrator.create_indexes()
        
        # Prepare and insert catalogue items
        items = migrator.prepare_catalogue_items()
        
        if not migrator.insert_catalogue_items(items):
            logger.error("Failed to insert catalogue items. Exiting.")
            sys.exit(1)
        
        # Verify migration
        if not migrator.verify_migration():
            logger.error("Migration verification failed. Please check the data.")
            sys.exit(1)
        
        # Print summary
        migrator.print_summary()
        
        logger.info("Catalogue migration completed successfully! 🎉")
        
    except KeyboardInterrupt:
        logger.info("Migration interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error during migration: {e}")
        sys.exit(1)
    finally:
        migrator.disconnect()


if __name__ == "__main__":
    main() 