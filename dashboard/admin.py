from django.contrib import admin
from .models import Brand, Product, ProductOffer, Cart, CartItem, Wishlist, PriceAlert, Order, OrderItem

class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'logo_url')
    search_fields = ('name',)

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'category', 'subcategory')
    search_fields = ('name', 'brand__name')
    list_filter = ('brand', 'category', 'subcategory')

class ProductOfferAdmin(admin.ModelAdmin):
    list_display = ('product', 'site', 'price', 'rating')
    search_fields = ('product__name', 'site')
    list_filter = ('site', 'rating')

class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')

class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product_offer', 'quantity')

class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'added_at')
    search_fields = ('user__username', 'product__name')

class PriceAlertAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'desired_price', 'is_active')
    search_fields = ('user__username', 'product__name')
    list_filter = ('is_active',)

class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'user', 'total_price', 'status', 'created_at')
    search_fields = ('order_id', 'user__username')
    list_filter = ('status',)

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product_offer', 'quantity', 'price')

admin.site.register(Brand, BrandAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductOffer, ProductOfferAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)
admin.site.register(Wishlist, WishlistAdmin)
admin.site.register(PriceAlert, PriceAlertAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
