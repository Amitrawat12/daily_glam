from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
import json
from dashboard.views import get_base_context
from dashboard.models import Product, Brand, ProductOffer
from django.db.models import Min, Max

def compare_home(request):
    """Displays the main page for the compare feature, showing product categories."""
    context = get_base_context()
    if 'compare_list' in request.session:
        del request.session['compare_list']
        request.session.modified = True
    return render(request, 'compare/compare.html', context)

def category_view(request, category_name):
    """Displays products from a selected category, with subcategory and brand filters."""
    context = get_base_context()
    
    products = Product.objects.filter(category=category_name).prefetch_related('offers', 'brand')
    subcategories = products.values('subcategory').distinct().order_by('subcategory')
    brands = Brand.objects.filter(products__in=products).distinct().order_by('name')

    price_stats = ProductOffer.objects.filter(product__in=products).aggregate(min_price=Min('price'), max_price=Max('price'))

    context.update({
        'category_name': category_name,
        'products': products,
        'subcategories': subcategories,
        'filter_brands': brands,
        'min_price': price_stats['min_price'] or 0,
        'max_price': price_stats['max_price'] or 100,
    })
    return render(request, 'compare/category.html', context)

def add_to_compare(request):
    """Adds a product to the comparison list in the session."""
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = data.get('product_id')
        offer_id = data.get('offer_id')

        if not product_id and not offer_id:
            return JsonResponse({'status': 'error', 'message': 'Product or offer ID is required.'}, status=400)

        product = None
        if offer_id:
            try:
                offer = ProductOffer.objects.select_related('product__brand').get(id=offer_id)
                product = offer.product
            except ProductOffer.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Invalid offer ID.'}, status=404)
        elif product_id:
            try:
                product = Product.objects.prefetch_related('offers', 'brand').get(id=product_id)
            except Product.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Invalid product ID.'}, status=404)

        if not product:
             return JsonResponse({'status': 'error', 'message': 'Product not found.'}, status=404)

        compare_list = request.session.get('compare_list', [])

        if not any(p['id'] == product.id for p in compare_list):
            if len(compare_list) < 4:
                offers_data = []
                for offer in product.offers.all():
                    offers_data.append({
                        'site': offer.site,
                        'price': str(offer.price),
                        'url': offer.url,
                        'rating': str(offer.rating) if offer.rating else None,
                        'review': offer.review
                    })

                product_data = {
                    'id': product.id,
                    'name': product.name,
                    'brand': product.brand.name,
                    'image': product.image.url if hasattr(product.image, 'url') else str(product.image),
                    'description': product.description,
                    'offers': offers_data
                }
                compare_list.append(product_data)
                request.session['compare_list'] = compare_list
                request.session.modified = True

                return JsonResponse({
                    'status': 'success',
                    'message': 'Product added to comparison.',
                    'compare_item_count': len(compare_list)
                })
            else:
                return JsonResponse({'status': 'error', 'message': 'You can only compare up to 4 products.'})
        else:
            return JsonResponse({'status': 'info', 'message': 'Product is already in your comparison list.'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)

def compare_page_view(request):
    context = get_base_context()
    compare_list = request.session.get('compare_list', [])
    context['compare_list'] = compare_list
    return render(request, 'compare/compare_page.html', context)

def remove_from_compare(request, product_id):
    compare_list = request.session.get('compare_list', [])
    updated_list = [item for item in compare_list if item.get('id') != int(product_id)]
    request.session['compare_list'] = updated_list
    request.session.modified = True
    return redirect('compare:compare_page')

def clear_compare(request):
    if 'compare_list' in request.session:
        del request.session['compare_list']
        request.session.modified = True
    return redirect('compare:compare_page')

def product_detail_view(request, product_id):
    context = get_base_context()
    product = get_object_or_404(Product.objects.prefetch_related('offers'), id=product_id)
    context.update({
        'product': product,
    })
    return render(request, 'compare/product_detail.html', context)
