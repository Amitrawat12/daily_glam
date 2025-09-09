from django.contrib import admin
from .models import Brand, Product, Cart, CartItem

# Register your models here.
admin.site.register(Brand)
admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(CartItem)
