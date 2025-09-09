import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from compare.models import SavedComparison, ComparisonItem
from django.contrib.auth.models import User
import http.client
import json
import os
import re
from django.conf import settings

# --- Advanced Scraping Patch ---
# This monkey-patches the HTTP client to be less strict about the number of headers.
# This is a common workaround for scraping sites with non-standard responses.
http.client._MAXHEADERS = 1000
# --- End of Patch ---

class Command(BaseCommand):
    help = 'Scrapes multiple products from a JSON file and saves them to the database'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("--- Starting the Product Scraping Process ---"))

        # Load the list of products to scrape
        products_json_path = os.path.join(settings.BASE_DIR, 'dashboard/static', 'data', 'products_to_scrape.json')
        try:
            with open(products_json_path, 'r') as f:
                products_to_scrape = json.load(f)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"CRITICAL: Scraping list not found at {products_json_path}"))
            return

        user = User.objects.first()
        if not user:
            self.stdout.write(self.style.ERROR("CRITICAL: No users found in the database. Please create a user first."))
            return

        # Loop through each product in the JSON file
        for product_data in products_to_scrape:
            product_name = product_data['name']
            self.stdout.write(f"\nProcessing product: '{product_name}'")

            # Create a new comparison object for this product
            comparison, created = SavedComparison.objects.update_or_create(
                name=product_name,
                defaults={'user': user, 'category': product_data.get('category', 'default')}
            )
            comparison.items.all().delete()

            # Scrape each URL for the current product
            for url_info in product_data['urls']:
                self.scrape_site(
                    comparison=comparison,
                    product_info=product_data,
                    url=url_info['url'],
                    site_name=url_info['site'],
                    price_selector=url_info['price_selector']
                )

        self.stdout.write(self.style.SUCCESS("\n--- Scraping process completed! ---"))

    def scrape_site(self, comparison, product_info, url, site_name, price_selector):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        try:
            with requests.Session() as s:
                s.headers.update(headers)
                response = s.get(url)
                response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")
            price_element = soup.select_one(price_selector)
            
            if price_element:
                price_text = price_element.text.strip()
                # Use a regular expression to find the first number in the string
                match = re.search(r'\d[\d,.]*\d', price_text)
                if match:
                    cleaned_price = match.group(0).replace(',', '')
                    price = float(cleaned_price)
                    
                    ComparisonItem.objects.create(
                        comparison=comparison,
                        product_id=f"{site_name.lower()}_{comparison.id}",
                        name=product_info['name'],
                        brand=product_info['brand'],
                        price=price,
                        image=product_info['image'],
                        site=site_name,
                        url=url
                    )
                    self.stdout.write(self.style.SUCCESS(f"  - [SUCCESS] Scraped {site_name}: ₹{price}"))
                else:
                    self.stdout.write(self.style.WARNING(f"  - [WARNING] Found the price element, but could not extract a number from the text: '{price_text}'"))
            else:
                self.stdout.write(self.style.WARNING(f"  - [WARNING] Could not find the price element for {site_name} using selector '{price_selector}'. The site's layout may have changed."))

        except requests.exceptions.RequestException as e:
            self.stdout.write(self.style.ERROR(f"  - [FAILED] Could not fetch page for {site_name}. URL may be invalid or the site may be blocking requests. Error: {e}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  - [FAILED] An unexpected error occurred while scraping {site_name}: {e}"))
