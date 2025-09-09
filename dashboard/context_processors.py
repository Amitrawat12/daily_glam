from .models import Cart, Wishlist, PriceAlert

def cart_context(request):
    cart_item_count = 0
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            cart_item_count = cart.items.count()
        except Cart.DoesNotExist:
            pass
    return {'cart_context': {'cart_item_count': cart_item_count}}

def wishlist_context(request):
    wishlist_item_count = 0
    if request.user.is_authenticated:
        wishlist_item_count = Wishlist.objects.filter(user=request.user).count()
    return {'wishlist_context': {'wishlist_item_count': wishlist_item_count}}

def price_alert_context(request):
    price_alert_count = 0
    if request.user.is_authenticated:
        price_alert_count = PriceAlert.objects.filter(user=request.user, is_active=True).count()
    return {'price_alert_context': {'price_alert_count': price_alert_count}}
