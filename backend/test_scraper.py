#!/usr/bin/env python3
"""
Test script for Zara scraper
"""

from zara_scraper import ZaraScraper
import logging
import json

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_scraper():
    """Test the scraper with a small sample."""
    scraper = ZaraScraper()
    
    # Test with smaller counts for testing
    target_counts = {
        'male_shirts': 2,
        'female_shirts': 2,
        'male_pants': 2,
        'female_pants': 2,
        'dresses': 3
    }
    
    logger.info("Testing Zara scraper with sample data...")
    
    # Scrape products
    products = scraper.scrape_products(target_counts)
    
    # Save to JSON
    scraper.save_to_json(products, 'test_zara_products.json')
    
    logger.info(f"Test completed! Found {len(products)} products total.")
    
    # Print summary
    categories = {}
    for product in products:
        cat = product['category']
        categories[cat] = categories.get(cat, 0) + 1
    
    logger.info("Product summary:")
    for category, count in categories.items():
        logger.info(f"  {category}: {count}")
    
    # Print first product as example
    if products:
        logger.info("Example product:")
        logger.info(json.dumps(products[0], indent=2))

if __name__ == "__main__":
    test_scraper() 