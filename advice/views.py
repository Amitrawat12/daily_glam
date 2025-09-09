from django.shortcuts import render, redirect
from django.http import JsonResponse
import json
import os
import random
from django.conf import settings
from django.core.files.storage import default_storage
from dashboard.views import get_base_context

# --- Bank of 30 Pre-written AI Responses ---
AI_RESPONSES = [
    # Dehydration & Dullness
    {'detected_concern': 'Mild Dehydration', 'suggested_products': [
        {'name': 'Hyaluronic Acid Serum', 'reason': 'To deeply hydrate and plump the skin.'},
        {'name': 'Ceramide-Rich Moisturizer', 'reason': 'To lock in moisture and support the skin barrier.'},
        {'name': 'Creamy Hydrating Cleanser', 'reason': 'To cleanse without stripping natural oils.'}
    ]},
    {'detected_concern': 'Signs of Fatigue', 'suggested_products': [
        {'name': 'Caffeine Eye Cream', 'reason': 'To reduce puffiness and dark circles.'},
        {'name': 'Vitamin C Serum', 'reason': 'To brighten the complexion and fight free radicals.'},
        {'name': 'Cooling Gel Mask', 'reason': 'To refresh and invigorate tired-looking skin.'}
    ]},
    {'detected_concern': 'Dull & Lifeless Skin', 'suggested_products': [
        {'name': 'AHA/BHA Exfoliating Cleanser', 'reason': 'To slough away dead skin cells and improve radiance.'},
        {'name': 'Niacinamide 10% Serum', 'reason': 'To improve overall skin texture and brightness.'},
        {'name': 'Moisturizer with SPF 30', 'reason': 'To protect skin from dulling UV rays.'}
    ]},
    # Acne & Oiliness
    {'detected_concern': 'Minor Breakouts & Clogged Pores', 'suggested_products': [
        {'name': 'Salicylic Acid Cleanser', 'reason': 'To exfoliate inside the pores and reduce breakouts.'},
        {'name': 'Clay Mask', 'reason': 'To draw out impurities and absorb excess oil.'},
        {'name': 'Lightweight, Oil-Free Moisturizer', 'reason': 'To hydrate without clogging pores.'}
    ]},
    {'detected_concern': 'Excess Sebum Production', 'suggested_products': [
        {'name': 'Foaming Gel Cleanser', 'reason': 'To effectively remove excess oil and grime.'},
        {'name': 'Witch Hazel Toner', 'reason': 'To minimize the appearance of pores.'},
        {'name': 'Mattifying Sunscreen', 'reason': 'To control shine throughout the day.'}
    ]},
    # Aging & Texture
    {'detected_concern': 'Fine Lines & Texture', 'suggested_products': [
        {'name': 'Gentle Retinoid Serum', 'reason': 'To promote cell turnover and soften fine lines.'},
        {'name': 'Peptide-Infused Moisturizer', 'reason': 'To support collagen and improve firmness.'},
        {'name': 'Hydrating Eye Cream', 'reason': 'To nourish the delicate eye area.'}
    ]},
    {'detected_concern': 'Loss of Firmness', 'suggested_products': [
        {'name': 'Collagen-Boosting Serum', 'reason': 'To help improve skin elasticity.'},
        {'name': 'Gua Sha Tool', 'reason': 'For facial massage to promote circulation and lift.'},
        {'name': 'Rich Night Cream', 'reason': 'To deeply nourish and repair skin overnight.'}
    ]},
    # Sensitivity & Redness
    {'detected_concern': 'General Redness & Irritation', 'suggested_products': [
        {'name': 'Centella Asiatica (Cica) Balm', 'reason': 'To soothe and calm irritated skin.'},
        {'name': 'Oat Kernel Cleanser', 'reason': 'A very gentle, non-irritating cleansing option.'},
        {'name': 'Mineral-Based Sunscreen', 'reason': 'Less likely to cause irritation than chemical sunscreens.'}
    ]},
    # Pigmentation
    {'detected_concern': 'Slightly Uneven Skin Tone', 'suggested_products': [
        {'name': 'Azelaic Acid Suspension', 'reason': 'To target redness and uneven tone.'},
        {'name': 'Vitamin C Powder', 'reason': 'Can be mixed with serums for a potent antioxidant boost.'},
        {'name': 'Daily SPF 50+', 'reason': 'Crucial for preventing further pigmentation.'}
    ]},
    # General Health
    {'detected_concern': 'Healthy but needs Maintenance', 'suggested_products': [
        {'name': 'pH-Balanced Gentle Cleanser', 'reason': 'To maintain the skin’s natural barrier.'},
        {'name': 'Antioxidant Serum (e.g., Ferulic Acid)', 'reason': 'To protect against daily environmental damage.'},
        {'name': 'Dependable Daily Moisturizer', 'reason': 'To keep skin hydrated and balanced.'}
    ]},
] * 3 # Duplicate the 10 unique responses to make a list of 30

def beauty_advice_view(request):
    context = get_base_context()
    return render(request, 'advice/advice.html', context)

def get_ai_recommendations(request):
    if request.method == 'POST':
        # For now, we just return a random response.
        # The user's input is ignored in this simplified version.
        response_data = random.choice(AI_RESPONSES)
        
        # Format the response as a markdown-like string for the frontend
        recommendation_text = f"### Detected Concern: {response_data['detected_concern']} ###\n\n"
        for product in response_data['suggested_products']:
            recommendation_text += f"* {product['name']}: {product['reason']}\n"
            
        return JsonResponse({'recommendations': recommendation_text})
    
    return JsonResponse({'error': 'Invalid request method.'}, status=405)

def visual_advice_view(request):
    """Handles the visual advice page and image upload."""
    context = get_base_context()
    
    if request.method == 'POST' and request.FILES.get('user_image'):
        uploaded_image = request.FILES['user_image']
        
        # Save the uploaded image to the media directory
        file_name = default_storage.save(uploaded_image.name, uploaded_image)
        file_url = default_storage.url(file_name)

        # --- Select a Random Pre-written Response ---
        random_response = random.choice(AI_RESPONSES)
        
        recommendations = {
            'detected_concern': random_response['detected_concern'],
            'suggested_products': random_response['suggested_products'],
            'image_name': uploaded_image.name,
            'image_url': file_url  # Add the image URL to the response
        }
        
        context['recommendations'] = recommendations
        return render(request, 'advice/visual_advice.html', context)

    return render(request, 'advice/visual_advice.html', context)
