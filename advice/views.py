
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from django.core.files.storage import default_storage
from dashboard.views import get_base_context
import google.generativeai as genai
import json
from PIL import Image

# Configure the Gemini API
try:
    genai.configure(api_key=settings.GEMINI_API_KEY)
except AttributeError:
    # Handle the case where the API key is not set
    genai.configure(api_key='YOUR_GEMINI_API_KEY') # Fallback, but will fail if not replaced

def beauty_advice_view(request):
    context = get_base_context()
    return render(request, 'advice/advice.html', context)

def get_ai_recommendations(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            skin_type = data.get('skin_type')
            concerns = ", ".join(data.get('skin_concerns', []))

            # Consolidate all other answers into a single preferences string
            preferences_list = []
            if data.get('age_range'):
                preferences_list.append(f"Age range: {data.get('age_range')}")
            if data.get('gender'):
                preferences_list.append(f"Gender: {data.get('gender')}")
            if data.get('skin_tone'):
                preferences_list.append(f"Skin tone: {data.get('skin_tone')}")
            if data.get('scent_preference'):
                preferences_list.append(f"Scent: {data.get('scent_preference')}")
            if data.get('beard_care'):
                preferences_list.append(f"Beard care: {data.get('beard_care')}")
            preferences = ", ".join(preferences_list)

            if not skin_type or not concerns:
                return JsonResponse({'error': 'Skin type and concerns are required.'}, status=400)

            # Create a prompt for the Gemini API
            prompt = f"""
            Act as a virtual skincare consultant for a beauty platform called Daily Glam.
            A user has provided the following information from a quiz:
            - Skin Type: {skin_type}
            - Primary Concerns: {concerns}
            - Other Preferences: {preferences}

            Based on this, please provide a personalized skincare routine. Your response should be in a JSON format with two keys:
            1. "detected_concern": A summary of the user's main skin issues based on their concerns.
            2. "suggested_products": A list of 3-4 product suggestions. Each product should be an object with two keys: "name" (the type of product, e.g., 'Hydrating Cleanser') and "reason" (a brief explanation of why it's recommended).

            Example Response:
            {{
                "detected_concern": "Dehydrated skin with a focus on anti-aging.",
                "suggested_products": [
                    {{"name": "Gentle Hydrating Cleanser", "reason": "To cleanse without stripping moisture."}},
                    {{"name": "Hyaluronic Acid Serum", "reason": "To boost hydration and plump the skin."}},
                    {{"name": "Retinoid Cream", "reason": "To address fine lines and promote cell turnover."}}
                ]
            }}
            """

            model = genai.GenerativeModel('models/gemini-1.5-flash-latest')
            response = model.generate_content(prompt)

            # Clean up the response from the model
            cleaned_response_text = response.text.strip().replace('```json', '').replace('```', '')
            recommendations = json.loads(cleaned_response_text)

            return JsonResponse(recommendations)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON in request.'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'An error occurred with the AI service: {str(e)}'}, status=500)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)

def visual_advice_view(request):
    context = get_base_context()

    if request.method == 'POST' and request.FILES.get('user_image'):
        uploaded_image_file = request.FILES['user_image']

        try:
            # Verify the image
            img = Image.open(uploaded_image_file)
            img.verify() # Check if it's a valid image

            # Re-open the image to work with it after verification
            uploaded_image_file.seek(0)
            img = Image.open(uploaded_image_file)

            # Create a prompt for the Gemini Vision API
            prompt = f"""
            Analyze the user's uploaded skin image. Identify the primary skin concerns visible (e.g., redness, acne, fine lines, uneven texture, dark spots). 
            Based on your analysis, act as a virtual skincare consultant for Daily Glam and recommend a simple, effective skincare routine.
            Your response must be in a JSON format with two keys:
            1. "detected_concern": A string summarizing the main visible skin concern.
            2. "suggested_products": A list of 2-3 product suggestions. Each product should be an object with "name" (e.g., 'Soothing Cleanser') and "reason".

            Example:
            {{
                "detected_concern": "Visible redness and slight irritation on the cheeks.",
                "suggested_products": [
                    {{"name": "Calming Cica Cleanser", "reason": "To gently cleanse without further irritating the skin."}},
                    {{"name": "Niacinamide Serum", "reason": "To help reduce redness and strengthen the skin barrier."}}
                ]
            }}
            """

            model = genai.GenerativeModel('models/gemini-1.5-flash-latest')
            response = model.generate_content([prompt, img])

            # Clean and parse the JSON response
            cleaned_response_text = response.text.strip().replace('```json', '').replace('```', '')
            recommendations = json.loads(cleaned_response_text)

            # Save the image and get its URL for display
            file_name = default_storage.save(uploaded_image_file.name, uploaded_image_file)
            file_url = default_storage.url(file_name)

            # Add image info to the recommendations dictionary
            recommendations['image_url'] = file_url
            recommendations['image_name'] = file_name
            context['recommendations'] = recommendations

        except Exception as e:
            context['error'] = f"Could not analyze the image. Please try another one. Error: {str(e)}"

    return render(request, 'advice/visual_advice.html', context)
