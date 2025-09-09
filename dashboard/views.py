from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.db.models import Min, Max
import json
import os
import re
import math
from django.conf import settings
from .models import Brand, Product, ProductOffer, Cart, CartItem, Wishlist, PriceAlert
from urllib.parse import quote_plus

def normalize_brand_name(name):
    """Normalizes a brand name or filename for easier matching."""
    name = os.path.splitext(name)[0]
    return re.sub(r'[^a-z0-9]', '', name.lower())

def get_base_context():
    """Loads the context required by the base template, fetching data from the database."""
    brands = Brand.objects.all().order_by('name')
    
    num_brands = len(brands)
    num_columns = 4
    brand_columns = []
    if num_brands > 0:
        brands_per_column = math.ceil(num_brands / num_columns)
        brand_columns = [brands[i:i + brands_per_column] for i in range(0, num_brands, brands_per_column)]

    category_names = Product.objects.values_list('category', flat=True).filter(category__isnull=False).exclude(category__exact='').distinct().order_by('category')
    categories = [{'name': name} for name in category_names]

    return {
        'brands': brands, 
        'brand_columns': brand_columns, 
        'categories': categories
    }

@login_required
def dashboard_home(request):
    context = get_base_context()
    featured_brands = Brand.objects.all()[:18]
    context['featured_brands'] = featured_brands
    return render(request, 'dashboard/dashboard.html', context)

@login_required
def all_brands_view(request):
    context = get_base_context()
    return render(request, 'dashboard/all_brands.html', context)

@login_required
def brand_detail_view(request, brand_name):
    context = get_base_context()
    brand = get_object_or_404(Brand, name=brand_name)
    
    products = Product.objects.filter(brand=brand).prefetch_related('offers')
    subcategories = products.values_list('subcategory', flat=True).distinct().order_by('subcategory')

    all_min_prices = [p.offers.first().price for p in products if p.offers.exists()]
    min_price = min(all_min_prices) if all_min_prices else 0
    max_price = max(all_min_prices) if all_min_prices else 100

    context.update({
        'brand_name': brand_name,
        'products': products,
        'subcategories': subcategories,
        'min_price': min_price,
        'max_price': max_price,
    })
    return render(request, 'dashboard/brand_detail.html', context)

@login_required
def category_detail_view(request, category_name):
    context = get_base_context()
    products = Product.objects.filter(category=category_name).prefetch_related('offers', 'brand')

    all_min_prices = [p.offers.first().price for p in products if p.offers.exists()]
    min_price = min(all_min_prices) if all_min_prices else 0
    max_price = max(all_min_prices) if all_min_prices else 100

    context.update({
        'category_name': category_name,
        'products': products,
        'min_price': min_price,
        'max_price': max_price,
    })
    return render(request, 'dashboard/category_detail.html', context)

@login_required
def cart_view(request):
    context = get_base_context()
    cart, created = Cart.objects.get_or_create(user=request.user)
    total_price = sum(item.product_offer.price * item.quantity for item in cart.items.all())

    context.update({
        'cart_items': cart.items.all(),
        'total_price': total_price
    })
    return render(request, 'dashboard/cart.html', context)

@login_required
def remove_from_cart_view(request, item_id):
    cart = Cart.objects.get(user=request.user)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    cart_item.delete()
    return redirect('dashboard:cart_view')

@login_required
def add_to_cart_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        offer_id = data.get('offer_id')

        if not offer_id:
            return JsonResponse({'status': 'error', 'message': 'Invalid offer ID'}, status=400)

        offer = get_object_or_404(ProductOffer, id=offer_id)
        cart, created = Cart.objects.get_or_create(user=request.user)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, 
            product_offer=offer, 
            defaults={'quantity': 1}
        )
        
        if not created:
            cart_item.quantity += 1
            cart_item.save()

        return JsonResponse({'status': 'success', 'cart_item_count': cart.items.count()})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

@login_required
def increase_cart_item_quantity(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.quantity += 1
    cart_item.save()
    return redirect('dashboard:cart_view')

@login_required
def decrease_cart_item_quantity(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('dashboard:cart_view')

@login_required
def checkout_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all()
    total_price = sum(item.product_offer.price * item.quantity for item in cart_items)

    if request.method == 'POST':
        email = request.POST.get('email')
        email_context = {
            'user': request.user,
            'cart_items': cart_items,
            'total_price': total_price
        }
        email_body = render_to_string('dashboard/order_confirmation_email.html', email_context)
        
        send_mail(
            'Your Daily Glam Order Confirmation',
            email_body,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )

        cart.items.all().delete()
        return redirect('dashboard:order_successful')

    context = get_base_context()
    context.update({
        'cart_items': cart_items,
        'total_price': total_price
    })
    return render(request, 'dashboard/checkout.html', context)

@login_required
def order_successful_view(request):
    return render(request, 'dashboard/order_successful.html')

@login_required
def wishlist_view(request):
    context = get_base_context()
    wishlist_items = Wishlist.objects.filter(user=request.user)
    context['wishlist_items'] = wishlist_items
    return render(request, 'dashboard/wishlist.html', context)

@login_required
def add_to_wishlist_view(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
        
        if created:
            message = 'Product added to your wishlist!'
        else:
            message = 'This product is already in your wishlist.'

        wishlist_count = Wishlist.objects.filter(user=request.user).count()

        return JsonResponse({
            'status': 'success' if created else 'info',
            'message': message,
            'wishlist_item_count': wishlist_count
        })
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)

@login_required
def remove_from_wishlist_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    Wishlist.objects.filter(user=request.user, product=product).delete()
    return redirect('dashboard:wishlist')

@login_required
def price_alert_view(request):
    price_alerts = PriceAlert.objects.filter(user=request.user)
    context = {
        'price_alerts': price_alerts
    }
    return render(request, 'dashboard/price_alert_list.html', context)

@login_required
def add_price_alert_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        desired_price = request.POST.get('desired_price')
        if desired_price:
            PriceAlert.objects.update_or_create(
                user=request.user, 
                product=product, 
                defaults={'desired_price': desired_price, 'is_active': True}
            )
            return JsonResponse({'status': 'success', 'message': 'Price alert has been set!'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Please provide a desired price.'}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)

@login_required
def remove_price_alert_view(request, alert_id):
    alert = get_object_or_404(PriceAlert, id=alert_id, user=request.user)
    alert.delete()
    return redirect('dashboard:price_alert_list')
