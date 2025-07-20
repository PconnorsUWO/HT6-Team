#!/usr/bin/env python3
"""
Zara Product Scraper
Scrapes Zara website to extract product information and organize it by category and gender.
"""

import requests
import json
import time
import os
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import random
from typing import Dict, List, Optional, Tuple
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ZaraScraper:
    def __init__(self):
        self.base_url = "https://www.zara.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Create directories for storing images
        self.image_dirs = {
            'male_shirts': 'images/male_shirts',
            'female_shirts': 'images/female_shirts', 
            'male_pants': 'images/male_pants',
            'female_pants': 'images/female_pants',
            'dresses': 'images/dresses'
        }
        
        for dir_path in self.image_dirs.values():
            os.makedirs(dir_path, exist_ok=True)
    
    def get_product_urls(self, category: str, gender: str, limit: int = 20) -> List[str]:
        """Get product URLs for a specific category and gender."""
        urls = []
        
        # Zara category mappings with the provided seed URLs
        category_mappings = {
            'shirts': {
                'male': 'https://www.zara.com/ca/en/man-shirts-l737.html?v1=2431994&regionGroupId=124',
                'female': 'https://www.zara.com/ca/en/woman-shirts-l1217.html?v1=2420369&regionGroupId=124'
            },
            'pants': {
                'male': 'https://www.zara.com/ca/en/man-trousers-l838.html?v1=2432096&regionGroupId=124', 
                'female': 'https://www.zara.com/ca/en/woman-trousers-l1335.html?v1=2420795&regionGroupId=124'
            },
            'dresses': {
                'female': 'https://www.zara.com/ca/en/woman-dresses-l1066.html?v1=2420896&regionGroupId=124'
            }
        }
        
        if category not in category_mappings:
            logger.error(f"Unknown category: {category}")
            return urls
            
        if gender not in category_mappings[category]:
            logger.error(f"Gender {gender} not available for category {category}")
            return urls
            
        category_url = category_mappings[category][gender]
        
        try:
            logger.info(f"Fetching products from: {category_url}")
            response = self.session.get(category_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find product links - look for product detail links
            # Zara uses various patterns for product URLs
            product_links = []
            
            # Pattern 1: Direct product links
            direct_links = soup.find_all('a', href=re.compile(r'p\d+\.html'))
            product_links.extend(direct_links)
            
            # Pattern 2: Product cards with data attributes
            product_cards = soup.find_all('a', {'data-qa-action': 'product-card'})
            product_links.extend(product_cards)
            
            # Pattern 3: Links with product IDs
            product_id_links = soup.find_all('a', href=re.compile(r'/ca/en/.*p\d+'))
            product_links.extend(product_id_links)
            
            # Remove duplicates and extract URLs
            seen_urls = set()
            for link in product_links:
                href = link.get('href')
                if href:
                    full_url = urljoin(self.base_url, href)
                    if full_url not in seen_urls:
                        urls.append(full_url)
                        seen_urls.add(full_url)
                        if len(urls) >= limit:
                            break
                    
            logger.info(f"Found {len(urls)} product URLs for {gender} {category}")
            
        except Exception as e:
            logger.error(f"Error fetching product URLs: {e}")
            
        return urls
    
    def extract_product_info(self, url: str) -> Optional[Dict]:
        """Extract product information from a product page."""
        try:
            logger.info(f"Scraping product: {url}")
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract product name - try multiple selectors
            name = "Unknown Product"
            name_selectors = [
                'h1.product-detail-info__header-name',
                'h1.product-detail-card-info__header-name',
                'h1[data-qa-action="product-detail-name"]',
                '.product-detail-info__header-name',
                '.product-detail-card-info__header-name'
            ]
            
            for selector in name_selectors:
                name_elem = soup.select_one(selector)
                if name_elem:
                    name = name_elem.get_text(strip=True)
                    break
            
            # Extract price - try multiple selectors
            price = 0.0
            price_selectors = [
                'span.price-current__amount',
                '.price-current__amount',
                '[data-qa-action="product-detail-price"]',
                '.product-detail-info__price-current',
                '.product-detail-card-info__price-current'
            ]
            
            for selector in price_selectors:
                price_elem = soup.select_one(selector)
                if price_elem:
                    price_text = price_elem.get_text(strip=True)
                    # Extract numeric value from price text
                    price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
                    if price_match:
                        price = float(price_match.group())
                        break
            
            # Extract description - try multiple selectors
            desc = ""
            desc_selectors = [
                'div.product-detail-description',
                '.product-detail-description',
                '.product-detail-info__description',
                '.product-detail-card-info__description',
                '[data-qa-action="product-detail-description"]'
            ]
            
            for selector in desc_selectors:
                desc_elem = soup.select_one(selector)
                if desc_elem:
                    # Try to find expandable content
                    desc_content = desc_elem.select_one('.expandable-text__inner-content')
                    if desc_content:
                        desc = desc_content.get_text(strip=True)
                    else:
                        desc = desc_elem.get_text(strip=True)
                    break
            
            # Extract sizes - try multiple selectors
            sizes = []
            size_selectors = [
                'button.product-detail-size-selector__size-list-item',
                '.product-detail-size-selector__size-list-item',
                '[data-qa-action="product-detail-size"]',
                '.product-detail-info__size-selector button',
                '.product-detail-card-info__size-selector button'
            ]
            
            for selector in size_selectors:
                size_elems = soup.select(selector)
                for size_elem in size_elems:
                    size_text = size_elem.get_text(strip=True)
                    if size_text and size_text not in sizes and len(size_text) <= 5:  # Filter out non-size text
                        sizes.append(size_text)
                if sizes:  # If we found sizes, break
                    break
            
            # Extract images from product-detail-view__extra-images and product-detail-view__secondary-content
            images = []
            
            # Main product images - try multiple selectors
            image_selectors = [
                'ul.product-detail-view__extra-images img',
                '.product-detail-view__extra-images img',
                '.product-detail-view__secondary-content img',
                '.product-detail-view__main-content img',
                '[data-qa-action="product-detail-image"]',
                '.product-detail-info__image img',
                '.product-detail-card-info__image img'
            ]
            
            for selector in image_selectors:
                img_elems = soup.select(selector)
                for img in img_elems:
                    src = img.get('src') or img.get('data-src')
                    if src:
                        # Convert to high resolution URL
                        high_res_src = self.convert_to_high_res(src)
                        if high_res_src not in images:
                            images.append(high_res_src)
                if images:  # If we found images, break
                    break
            
            # If no images found in specific sections, try to find any product images
            if not images:
                all_imgs = soup.find_all('img', src=re.compile(r'static\.zara\.net'))
                for img in all_imgs:
                    src = img.get('src')
                    if src and 'product' in src.lower():
                        high_res_src = self.convert_to_high_res(src)
                        if high_res_src not in images:
                            images.append(high_res_src)
            
            # Determine category based on URL or content
            category = self.determine_category(url, name, desc)
            
            # Determine gender based on URL
            gender = self.determine_gender(url)
            
            product_info = {
                "category": category,
                "desc": desc,
                "image_url": images[0] if images else "",
                "name": name,
                "price": price,
                "sizes_available": sizes,
                "gender": gender,
                "all_images": images
            }
            
            return product_info
            
        except Exception as e:
            logger.error(f"Error extracting product info from {url}: {e}")
            return None
    
    def convert_to_high_res(self, image_url: str) -> str:
        """Convert image URL to high resolution version."""
        # Zara image URL patterns
        if 'static.zara.net' in image_url:
            # Remove size parameters and add high resolution
            base_url = re.sub(r'\?.*$', '', image_url)
            return f"{base_url}?ts={int(time.time())}&w=1920"
        return image_url
    
    def determine_category(self, url: str, name: str, desc: str) -> str:
        """Determine product category based on URL, name, and description."""
        url_lower = url.lower()
        name_lower = name.lower()
        desc_lower = desc.lower()
        
        if 'dress' in url_lower or 'dress' in name_lower or 'dress' in desc_lower:
            return 'dresses'
        elif 'shirt' in url_lower or 'shirt' in name_lower or 'shirt' in desc_lower:
            return 'shirts'
        elif any(word in url_lower for word in ['trouser', 'pant', 'jean']) or \
             any(word in name_lower for word in ['trouser', 'pant', 'jean']) or \
             any(word in desc_lower for word in ['trouser', 'pant', 'jean']):
            return 'pants'
        else:
            # Default based on URL path
            if '/dresses' in url_lower:
                return 'dresses'
            elif '/shirts' in url_lower:
                return 'shirts'
            elif '/trousers' in url_lower or '/pants' in url_lower:
                return 'pants'
            else:
                return 'unknown'
    
    def determine_gender(self, url: str) -> str:
        """Determine product gender based on URL."""
        url_lower = url.lower()
        if '/man' in url_lower or '/men' in url_lower:
            return 'male'
        elif '/woman' in url_lower or '/women' in url_lower:
            return 'female'
        else:
            return 'unknown'
    
    def download_image(self, image_url: str, category: str, gender: str, product_name: str) -> str:
        """Download and save product image."""
        try:
            response = self.session.get(image_url)
            response.raise_for_status()
            
            # Clean product name for filename
            clean_name = re.sub(r'[^\w\s-]', '', product_name)
            clean_name = re.sub(r'[-\s]+', '-', clean_name)
            
            # Determine directory
            if category == 'dresses':
                dir_path = self.image_dirs['dresses']
            elif category == 'shirts':
                dir_path = self.image_dirs[f'{gender}_shirts']
            elif category == 'pants':
                dir_path = self.image_dirs[f'{gender}_pants']
            else:
                dir_path = 'images/other'
                os.makedirs(dir_path, exist_ok=True)
            
            # Generate filename
            timestamp = int(time.time())
            filename = f"{clean_name}_{timestamp}.jpg"
            filepath = os.path.join(dir_path, filename)
            
            # Save image
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Downloaded image: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error downloading image {image_url}: {e}")
            return ""
    
    def scrape_products(self, target_counts: Dict[str, int]) -> Dict:
        """Scrape products according to target counts."""
        all_products = []
        
        # Define scraping order
        scraping_tasks = [
            ('shirts', 'male', target_counts.get('male_shirts', 5)),
            ('shirts', 'female', target_counts.get('female_shirts', 5)),
            ('pants', 'male', target_counts.get('male_pants', 5)),
            ('pants', 'female', target_counts.get('female_pants', 5)),
            ('dresses', 'female', target_counts.get('dresses', 10))
        ]
        
        for category, gender, count in scraping_tasks:
            logger.info(f"Scraping {count} {gender} {category}")
            
            # Get product URLs
            urls = self.get_product_urls(category, gender, count * 2)  # Get more URLs in case some fail
            
            products_found = 0
            for url in urls:
                if products_found >= count:
                    break
                    
                product_info = self.extract_product_info(url)
                if product_info:
                    # Download images
                    if product_info['image_url']:
                        local_path = self.download_image(
                            product_info['image_url'], 
                            product_info['category'], 
                            product_info['gender'], 
                            product_info['name']
                        )
                        product_info['local_image_path'] = local_path
                    
                    # Remove internal fields for final output
                    final_product = {
                        "category": product_info['category'],
                        "desc": product_info['desc'],
                        "image_url": product_info['image_url'],
                        "name": product_info['name'],
                        "price": product_info['price'],
                        "sizes_available": product_info['sizes_available']
                    }
                    
                    all_products.append(final_product)
                    products_found += 1
                    
                    # Add delay to be respectful
                    time.sleep(random.uniform(1, 3))
            
            logger.info(f"Found {products_found} {gender} {category}")
        
        return all_products
    
    def save_to_json(self, products: List[Dict], filename: str = 'zara_products.json'):
        """Save products to JSON file."""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(products, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(products)} products to {filename}")
        except Exception as e:
            logger.error(f"Error saving to JSON: {e}")

def main():
    """Main function to run the scraper."""
    scraper = ZaraScraper()
    
    # Target counts for each category
    target_counts = {
        'male_shirts': 5,
        'female_shirts': 5,
        'male_pants': 5,
        'female_pants': 5,
        'dresses': 10
    }
    
    logger.info("Starting Zara product scraper...")
    
    # Scrape products
    products = scraper.scrape_products(target_counts)
    
    # Save to JSON
    scraper.save_to_json(products)
    
    logger.info(f"Scraping completed! Found {len(products)} products total.")
    
    # Print summary
    categories = {}
    for product in products:
        cat = product['category']
        categories[cat] = categories.get(cat, 0) + 1
    
    logger.info("Product summary:")
    for category, count in categories.items():
        logger.info(f"  {category}: {count}")

if __name__ == "__main__":
    main() 