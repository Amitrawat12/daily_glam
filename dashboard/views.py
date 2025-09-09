from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.db.models import Min, Max, Count, Q
from django.contrib import messages
import json
import os
import re
import math
from django.conf import settings
from .models import Brand, Product, ProductOffer, Cart, CartItem, Wishlist, PriceAlert, Order, OrderItem
from .forms import ContactForm
from urllib.parse import quote_plus

def normalize_brand_name(name):
    """Normalizes a brand name or filename for easier matching."""
    name = os.path.splitext(name)[0]
    return re.sub(r'[^a-z0-9]', '', name.lower())

def get_base_context():
    """Loads the context required by the base template, fetching data from the database."""
    brands = Brand.objects.annotate(num_products=Count('products')).filter(num_products__gt=0).order_by('name')
    
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
    featured_brands = Brand.objects.annotate(num_products=Count('products')).filter(num_products__gt=0).order_by('-num_products')[:18]
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
    products_for_brand = Product.objects.filter(brand=brand).prefetch_related('offers')

    # Get available subcategories for filtering
    available_subcategories = products_for_brand.values_list('subcategory', flat=True).distinct().order_by('subcategory')

    # Calculate min and max price for the entire brand
    price_range = products_for_brand.aggregate(min_price=Min('offers__price'), max_price=Max('offers__price'))
    min_price = price_range.get('min_price') or 0
    max_price = price_range.get('max_price') or 1000

    # Get filter parameters from request
    selected_subcategory = request.GET.get('subcategory')
    selected_rating = request.GET.get('rating')
    selected_max_price = request.GET.get('max_price', max_price)

    # Apply filters
    filtered_products = products_for_brand
    if selected_subcategory:
        filtered_products = filtered_products.filter(subcategory=selected_subcategory)
    if selected_rating:
        filtered_products = filtered_products.annotate(max_rating=Max('offers__rating')).filter(max_rating__gte=selected_rating)
    if selected_max_price:
        filtered_products = filtered_products.annotate(min_offer_price=Min('offers__price')).filter(min_offer_price__lte=selected_max_price)

    context.update({
        'brand_name': brand_name,
        'products': filtered_products,
        'available_subcategories': available_subcategories,
        'min_price': min_price,
        'max_price': max_price,
        'selected_subcategory': selected_subcategory,
        'selected_rating': selected_rating,
        'selected_max_price': selected_max_price,
    })
    return render(request, 'dashboard/brand_detail.html', context)

@login_required
def category_detail_view(request, category_name):
    context = get_base_context()
    products_in_category = Product.objects.filter(category=category_name).prefetch_related('offers', 'brand')

    # Get available brands and subcategories for filtering
    available_brands = Brand.objects.filter(products__in=products_in_category).distinct().order_by('name')
    available_subcategories = products_in_category.values_list('subcategory', flat=True).distinct().order_by('subcategory')

    # Calculate min and max price for the entire category
    price_range = products_in_category.aggregate(min_price=Min('offers__price'), max_price=Max('offers__price'))
    min_price = price_range.get('min_price') or 0
    max_price = price_range.get('max_price') or 1000

    # Get filter parameters from request
    selected_brands = request.GET.getlist('brand')
    selected_subcategory = request.GET.get('subcategory')
    selected_rating = request.GET.get('rating')
    selected_max_price = request.GET.get('max_price', max_price)

    # Apply filters
    filtered_products = products_in_category
    if selected_brands:
        filtered_products = filtered_products.filter(brand__name__in=selected_brands)
    if selected_subcategory:
        filtered_products = filtered_products.filter(subcategory=selected_subcategory)
    if selected_rating:
        filtered_products = filtered_products.annotate(max_rating=Max('offers__rating')).filter(max_rating__gte=selected_rating)
    if selected_max_price:
        filtered_products = filtered_products.annotate(min_offer_price=Min('offers__price')).filter(min_offer_price__lte=selected_max_price)

    context.update({
        'category_name': category_name,
        'products': filtered_products,
        'available_brands': available_brands,
        'available_subcategories': available_subcategories,
        'min_price': min_price,
        'max_price': max_price,
        'selected_brands': selected_brands,
        'selected_subcategory': selected_subcategory,
        'selected_rating': selected_rating,
        'selected_max_price': selected_max_price,
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

# ... (rest of the views remain the same)
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

        # Create the order
        order = Order.objects.create(
            user=request.user,
            total_price=total_price
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product_offer=item.product_offer,
                quantity=item.quantity,
                price=item.product_offer.price
            )

        email_context = {
            'user': request.user,
            'cart_items': cart_items,
            'total_price': total_price,
            'order': order
        }
        html_message = render_to_string('dashboard/order_confirmation_email.html', email_context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            f'Your Daily Glam Order Confirmation #{order.order_id}',
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
            html_message=html_message
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
def order_history_view(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    context = get_base_context()
    context['orders'] = orders
    return render(request, 'dashboard/order_history.html', context)

@login_required
def order_detail_view(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    context = get_base_context()
    context['order'] = order
    return render(request, 'dashboard/order_detail.html', context)

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

def faq_view(request):
    context = get_base_context()
    return render(request, 'dashboard/faq.html', context)

def return_policy_view(request):
    context = get_base_context()
    return render(request, 'dashboard/return_policy.html', context)

def contact_view(request):
    context = get_base_context()
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            from_email = form.cleaned_data['email']
            
            email_body = f"You have a new query from {form.cleaned_data['name']}.\n\n"
            email_body += f"Email: {from_email}\n\n"
            email_body += f"Message:\n{message}"

            try:
                send_mail(
                    f"[Contact Form] {subject}",
                    email_body,
                    settings.DEFAULT_FROM_EMAIL, # This will be your gmail address
                    [settings.EMAIL_HOST_USER], # Send to yourself
                    fail_silently=False,
                )
                messages.success(request, 'Your message has been sent successfully! We will get back to you shortly.')
                return redirect('dashboard:contact')
            except Exception as e:
                messages.error(request, f'An error occurred while sending your message: {e}')

    else:
        form = ContactForm()
    
    context['form'] = form
    return render(request, 'dashboard/contact.html', context)
