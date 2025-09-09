import json
import random
import os
from django.core.management.base import BaseCommand
from django.conf import settings

# --- Data for Generation ---
PRODUCT_ADJECTIVES = ['Luminous', 'Matte', 'Velvet', 'Silk', 'Radiant', 'Intense', 'Sheer', 'HD', 'Pro', 'Ultimate', '24H', 'Aqua']
PRODUCT_DESCRIPTIONS = [
    'A revolutionary formula that provides all-day coverage.',
    'Infused with natural ingredients for a healthy glow.',
    'The perfect addition to your daily beauty routine.',
    'Designed for all skin types, providing a flawless finish.',
    'A must-have for achieving a professional look.',
    'Lightweight and breathable, you\'ll forget you\'re wearing it.',
    'Dermatologist-tested and approved for sensitive skin.'
]
SITES = ['Nykaa', 'Amazon', 'Purplle', 'Flipkart']

class Command(BaseCommand):
    help = 'Generates a large, realistic dataset of products from brand_data.json and saves it to product.json.'

    def handle(self, *args, **kwargs):
        self.stdout.write('Generating realistic test product records from brand_data.json...')
        
        # --- Load Brand and Category Data ---
        brand_data_path = settings.BASE_DIR / 'dashboard' / 'static' / 'data' / 'brand_data.json'
        try:
            with open(brand_data_path, 'r') as f:
                brands_data = json.load(f)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'Error: brand_data.json not found at {brand_data_path}'))
            return

        products = []
        product_id = 1

        for brand_info in brands_data:
            brand_name = brand_info['brand']
            categories = brand_info['categories']
            
            # Create a flat list of all possible products for the brand
            possible_products = []
            for category, product_types in categories.items():
                for product_type in product_types:
                    possible_products.append((category, product_type))
            
            if not possible_products:
                continue

            # Generate 10 unique products for the brand
            for _ in range(10):
                category_name, product_noun = random.choice(possible_products)
                product_adj = random.choice(PRODUCT_ADJECTIVES)
                product_name = f"{brand_name} {product_adj} {product_noun}"

                # Generate offers
                offers = []
                num_offers = random.randint(1, 3)
                base_price = round(random.uniform(500.0, 8000.0), 2)

                for site in random.sample(SITES, k=num_offers):
                    price_variation = random.uniform(-0.05, 0.05)
                    offer_price = round(base_price * (1 + price_variation), 2)
                    
                    offers.append({
                        "site": site,
                        "price": offer_price,
                        "url": f"http://example.com/{site.lower()}/{product_name.replace(' ', '-').lower()}",
                        "rating": round(random.uniform(3.8, 5.0), 1),
                        "review": f"A great {product_noun} from {brand_name}."
                    })

                product_record = {
                    "id": product_id,
                    "name": product_name,
                    "brand": brand_name,
                    "description": f"A high-quality {product_noun} from {brand_name} to meet your beauty needs.",
                    "image": f"https://placehold.co/300x300/9E9E9E/ffffff?text={product_noun.replace(' ', '+')}",
                    "offers": offers
                }
                products.append(product_record)
                product_id += 1

        # --- Save to file ---
        output_path = settings.BASE_DIR / 'dashboard' / 'static' / 'data' / 'product.json'
        try:
            with open(output_path, 'w') as f:
                json.dump(products, f, indent=2)
            self.stdout.write(self.style.SUCCESS(f'Successfully generated {len(products)} products and saved to {output_path}'))
        except IOError as e:
            self.stdout.write(self.style.ERROR(f'Error writing to file: {e}'))
