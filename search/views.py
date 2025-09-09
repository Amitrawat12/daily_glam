from django.shortcuts import render
from django.http import JsonResponse
from dashboard.models import Product, Brand
from django.db.models import Q

def search_results(request):
    query = request.GET.get('q', '')
    products = Product.objects.filter(
        Q(name__icontains=query) | Q(brand__name__icontains=query)
    ).prefetch_related('offers', 'brand')
    
    context = {
        'query': query,
        'products': products,
    }
    return render(request, 'search/search_results.html', context)

def search_suggestions(request):
    query = request.GET.get('q', '')
    
    if not query:
        return JsonResponse({'brands': [], 'products': []})

    brands = Brand.objects.filter(name__icontains=query).values_list('name', flat=True)[:5]
    products = Product.objects.filter(name__icontains=query).values('id', 'name')[:5]

    return JsonResponse({
        'brands': list(brands),
        'products': list(products),
    })
