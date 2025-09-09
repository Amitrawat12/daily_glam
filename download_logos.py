import requests
import json
import os

# --- Configuration ---
BRAND_JSON_PATH = 'dashboard/static/data/brand.json'
LOGO_DIR = 'dashboard/static/dashboard/logos'

def download_logos():
    """Reads the brand data and downloads the logos for each brand."""
    print("Starting logo download process...")

    # Ensure the logo directory exists
    os.makedirs(LOGO_DIR, exist_ok=True)

    # Load the brand data (which is a simple list of strings)
    try:
        with open(BRAND_JSON_PATH, 'r') as f:
            brand_names = json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find the brand JSON file at '{BRAND_JSON_PATH}'")
        return

    # Headers to mimic a real browser visit
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    for brand_name in brand_names:
        # Create a URL-friendly version of the brand name
        url_slug = brand_name.lower().replace(' ', '-').replace('’', '').replace('.', '').replace("&", "and")
        
        # Handle special cases for known URL variations
        if 'loreal' in url_slug: url_slug = 'loreal-paris'
        if 'mac' in url_slug: url_slug = 'mac-cosmetics'
        if 'dior' in url_slug: url_slug = 'dior-3'
        if 'chanel' in url_slug: url_slug = 'chanel-2'
        if 'neutrogena' in url_slug: url_slug = 'neutrogena-2'
        if 'the-body-shop' in url_slug: url_slug = 'the-body-shop-1'
        if 'versace' in url_slug: url_slug = 'versace-1'
        if 'paco-rabanne' in url_slug: url_slug = 'paco-rabanne-2'
        if 'innisfree' in url_slug: url_slug = 'innisfree-1'

        # Define the local file path
        file_name = f"{url_slug}.svg"
        local_path = os.path.join(LOGO_DIR, file_name)

        if os.path.exists(local_path):
            print(f"- Logo for {brand_name} already exists. Skipping.")
            continue

        # Construct the direct download URL
        logo_url = f"https://cdn.worldvectorlogo.com/logos/{url_slug}.svg"

        print(f"- Downloading logo for {brand_name} from {logo_url}...")

        try:
            response = requests.get(logo_url, headers=headers)
            response.raise_for_status()

            with open(local_path, 'wb') as f:
                f.write(response.content)
            
            print(f"  -> Saved to {local_path}")

        except requests.exceptions.RequestException as e:
            print(f"  -> FAILED to download {brand_name}. Status: {e.response.status_code if e.response else 'N/A'}")
        except Exception as e:
            print(f"  -> An unexpected error occurred for {brand_name}: {e}")

    print("\nLogo download process complete.")

if __name__ == "__main__":
    download_logos()
