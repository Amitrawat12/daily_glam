from django.contrib import admin
from .models import Brand, Product, ProductOffer, Cart, CartItem, Wishlist, PriceAlert, Order, OrderItem

# Register your models here.
admin.site.register(Brand)
admin.site.register(Product)
admin.site.register(ProductOffer)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Wishlist)
admin.site.register(PriceAlert)
admin.site.register(Order)
admin.site.register(OrderItem)
