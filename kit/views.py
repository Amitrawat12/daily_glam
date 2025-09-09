from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
import json
from dashboard.models import Product, Brand, Cart, CartItem, ProductOffer
from django.db.models import Min, Max

def kit_home(request):
    """Displays the main page for the kit builder, showing product categories."""
    categories = Product.objects.values_list('category', flat=True).distinct().order_by('category')
    context = {
        'categories': [{'name': name} for name in categories]
    }
    return render(request, 'kit/kit.html', context)

def category_view(request, category_name):
    """Displays products from a selected category, with subcategory and brand filters, specifically for the kit builder."""
    products = Product.objects.filter(category=category_name).prefetch_related('offers', 'brand')
    subcategories = products.values('subcategory').distinct().order_by('subcategory')
    brands = Brand.objects.filter(products__in=products).distinct().order_by('name')
    price_stats = ProductOffer.objects.filter(product__in=products).aggregate(min_price=Min('price'), max_price=Max('price'))

    context = {
        'category_name': category_name,
        'products': products,
        'subcategories': subcategories,
        'filter_brands': brands,
        'min_price': price_stats['min_price'] or 0,
        'max_price': price_stats['max_price'] or 100,
    }
    return render(request, 'kit/category.html', context)

def add_to_kit(request):
    """Adds a specific product offer to the user's kit in the session, handling quantity."""
    if request.method == 'POST':
        data = json.loads(request.body)
        try:
            # Ensure offer_id is treated as an integer
            offer_id = int(data.get('offer_id'))
        except (ValueError, TypeError):
            return JsonResponse({'status': 'error', 'message': 'Invalid offer ID format'}, status=400)

        offer = get_object_or_404(ProductOffer.objects.select_related('product__brand'), id=offer_id)
        product = offer.product

        kit = request.session.get('kit', [])
        
        # Check if item already in kit
        for item in kit:
            if item.get('offer_id') == offer_id:
                item['quantity'] = item.get('quantity', 1) + 1
                break
        else: # Item not found, add it
            kit.append({
                'offer_id': offer.id,
                'product_id': product.id,
                'name': product.name,
                'price': str(offer.price),
                'image': product.image.url if hasattr(product.image, 'url') else str(product.image),
                'brand': product.brand.name,
                'site': offer.site,
                'quantity': 1
            })
        
        request.session['kit'] = kit
        request.session.modified = True

        return JsonResponse({'status': 'success', 'message': 'Product added to kit!', 'kit_item_count': len(kit)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

def view_kit(request):
    """Displays the items currently in the user's kit."""
    kit_items = request.session.get('kit', [])
    total_price = sum(float(item.get('price', 0)) * item.get('quantity', 1) for item in kit_items)

    context = {
        'kit_items': kit_items,
        'total_price': total_price
    }
    return render(request, 'kit/view_kit.html', context)

def increase_kit_item_quantity(request, offer_id):
    """Increases the quantity of an item in the kit."""
    kit = request.session.get('kit', [])
    for item in kit:
        if item.get('offer_id') == offer_id:
            item['quantity'] = item.get('quantity', 1) + 1
            break
    request.session['kit'] = kit
    request.session.modified = True
    return redirect('kit:kit_view')

def decrease_kit_item_quantity(request, offer_id):
    """Decreases the quantity of an item in the kit."""
    kit = request.session.get('kit', [])
    for item in kit:
        if item.get('offer_id') == offer_id:
            if item.get('quantity', 1) > 1:
                item['quantity'] -= 1
            else:
                # If quantity is 1, remove the item by not including it in the new list
                kit = [i for i in kit if i.get('offer_id') != offer_id]
            break
    request.session['kit'] = kit
    request.session.modified = True
    return redirect('kit:kit_view')

def clear_kit(request):
    """Clears all items from the user's kit in the session."""
    if 'kit' in request.session:
        del request.session['kit']
        request.session.modified = True
    return redirect('kit:kit_view')

def remove_from_kit(request, offer_id):
    """Removes a single product offer from the user's kit in the session."""
    kit = request.session.get('kit', [])
    updated_kit = [item for item in kit if item.get('offer_id') != offer_id]
    request.session['kit'] = updated_kit
    request.session.modified = True
    return redirect('kit:kit_view')

def add_kit_to_cart(request):
    """Adds all items from the user's kit to the main shopping cart."""
    kit_items = request.session.get('kit', [])
    if not kit_items:
        return redirect('kit:kit_view')

    cart, _ = Cart.objects.get_or_create(user=request.user)
    
    for item_data in kit_items:
        offer = get_object_or_404(ProductOffer, id=item_data['offer_id'])
        # Use get_or_create and then update quantity
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, 
            product_offer=offer,
            defaults={'quantity': item_data.get('quantity', 1)}
        )
        if not created:
            cart_item.quantity += item_data.get('quantity', 1)
            cart_item.save()

    if 'kit' in request.session:
        del request.session['kit']
        request.session.modified = True

    return redirect('dashboard:cart_view')
