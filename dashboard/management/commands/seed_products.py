import json
import os
import re
from django.core.management.base import BaseCommand
from django.conf import settings
from dashboard.models import Brand, Product, ProductOffer

def normalize_brand_name(name):
    """Normalizes a brand name or filename for easier matching."""
    name = os.path.splitext(name)[0]
    return re.sub(r'[^a-z0-9]', '', name.lower())

class Command(BaseCommand):
    help = 'Seeds the database with product data from a consolidated product.json file.'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding database from consolidated product.json...')

        # --- Clear existing product data ONLY ---
        ProductOffer.objects.all().delete()
        Product.objects.all().delete()
        self.stdout.write('Cleared existing products and offers. Brands will be preserved.')

        # --- Load Data ---
        product_json_path = settings.BASE_DIR / 'dashboard' / 'static' / 'data' / 'product.json'
        categories_json_path = settings.BASE_DIR / 'dashboard' / 'static' / 'data' / 'categories.json'

        try:
            with open(product_json_path, 'r') as f:
                products_data = json.load(f)
            with open(categories_json_path, 'r') as f:
                categories_data = json.load(f)
        except FileNotFoundError as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}. Make sure product.json and categories.json exist.'))
            return

        # --- Prepare category mapping ---
        category_pairs = []
        for category in categories_data:
            for subcategory in category.get('sub_categories', []):
                category_pairs.append((category['name'], subcategory['name']))

        if not category_pairs:
            self.stdout.write(self.style.ERROR('No categories or subcategories found in categories.json. Aborting.'))
            return

        # --- Logo finding logic ---
        logo_dir_path = settings.BASE_DIR / 'dashboard' / 'static' / 'dashboard' / 'logos'
        logo_map = {}
        if os.path.exists(logo_dir_path):
            for filename in os.listdir(logo_dir_path):
                if filename.startswith('.') or filename == '.gitkeep':
                    continue
                normalized_name = normalize_brand_name(filename)
                logo_map[normalized_name] = f"dashboard/logos/{filename}"

        # --- Create brands, products, and offers ---
        for i, product_data in enumerate(products_data):
            brand_name = product_data.get('brand')
            if not brand_name:
                self.stdout.write(self.style.WARNING(f"Skipping product with no brand: {product_data.get('name')}"))
                continue

            # Use get_or_create to avoid deleting existing brands
            brand, created = Brand.objects.get_or_create(name=brand_name)

            if created:
                self.stdout.write(f'Created new brand: {brand_name}')
                normalized_brand = normalize_brand_name(brand_name)
                logo_url = logo_map.get(normalized_brand)
                if logo_url:
                    brand.logo_url = logo_url
                    brand.save()

            # Assign category and subcategory cyclically
            cat, subcat = category_pairs[i % len(category_pairs)]

            product = Product.objects.create(
                name=product_data['name'],
                brand=brand,
                description=product_data.get('description', 'No description available.'),
                image=product_data.get('image', 'default.jpg'),
                category=cat,
                subcategory=subcat,
            )

            # Create offers directly from the 'offers' list in the JSON
            offers = product_data.get('offers', [])
            if not offers:
                self.stdout.write(self.style.WARNING(f"No offers found for product: {product.name}"))
                continue

            for offer_data in offers:
                ProductOffer.objects.create(
                    product=product,
                    site=offer_data.get('site'),
                    price=offer_data.get('price'),
                    url=offer_data.get('url'),
                    rating=offer_data.get('rating'),
                    review=offer_data.get('review')
                )

        self.stdout.write(self.style.SUCCESS('Database seeded successfully from consolidated product.json!'))
