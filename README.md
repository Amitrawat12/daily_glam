# Daily Glam: AI-Powered Beauty Product Comparison

Daily Glam is a modern, AI-driven web application designed to help users find the best prices and products for their beauty needs. It features a sophisticated price comparison engine, personalized AI-powered skincare recommendations, and a clean, intuitive user interface.

## Features

*   **AI-Powered Beauty Advice:** Get personalized skincare recommendations through an interactive quiz or by uploading a photo for visual analysis.
*   **Comprehensive Product Catalog:** Browse and filter a wide range of beauty products from top brands like L'Oreal, Maybelline, and more.
*   **Advanced Filtering:** Easily narrow down products by brand, category, subcategory, price range, and user rating.
*   **Real-Time Price Comparison:** View and compare prices for the same product across multiple online retailers like Amazon, Nykaa, and Flipkart.
*   **Personalized User Accounts:** Users can register, log in, and manage their profiles.
*   **Shopping Cart & Wishlist:** Save products for later in your wishlist or add them to your cart directly from the product pages.
*   **Contact Form:** A functional contact form that sends user queries directly to the site administrator's email.
*   **Static Pages:** Includes informative FAQ and Return Policy pages.

## Getting Started

Follow these instructions to get a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

*   Python 3.8+
*   Pip (Python package installer)

### Installation

1.  **Clone the repository:**
    ```sh
    git clone <your-repository-url>
    cd Backend
    ```

2.  **Create and activate a virtual environment:**
    ```sh
    python -m venv .venv
    source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
    ```

3.  **Install the required packages:**
    ```sh
    pip install -r requirements.txt
    ```

4.  **Set up your environment variables:**
    You will need to configure your email and AI API keys in `daily_glam/settings.py`:
    *   `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD`: For sending emails.
    *   `GEMINI_API_KEY`: For the AI recommendation features.

5.  **Run the database migrations:**
    ```sh
    python manage.py migrate
    ```

6.  **Run the development server:**
    ```sh
    python manage.py runserver
    ```

    The application will be available at `http://127.0.0.1:8000/`.

## Core Technologies

*   **Backend:** Django, Python
*   **Frontend:** HTML, CSS, Bootstrap, JavaScript
*   **Database:** SQLite3 (for development)
*   **AI:** Google Gemini
