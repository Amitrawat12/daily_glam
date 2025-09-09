from django.urls import path
from .views import (
    dashboard_home, all_brands_view, brand_detail_view, 
    cart_view, remove_from_cart_view, add_to_cart_view, 
    checkout_view, order_successful_view, category_detail_view,
    wishlist_view, add_to_wishlist_view, remove_from_wishlist_view,
    price_alert_view, add_price_alert_view, remove_price_alert_view,
    increase_cart_item_quantity, decrease_cart_item_quantity
)
from accounts.views import custom_logout_view

app_name = 'dashboard'

urlpatterns = [
    path('', dashboard_home, name='dashboard_home'),
    path('logout/', custom_logout_view, name='logout'),
    path('brands/', all_brands_view, name='all_brands'),
    path('brand/<str:brand_name>/', brand_detail_view, name='brand_detail'),
    path('category/<str:category_name>/', category_detail_view, name='category_detail'),
    path('cart/', cart_view, name='cart_view'),
    path('cart/remove/<int:item_id>/', remove_from_cart_view, name='remove_from_cart'),
    path('add-to-cart/', add_to_cart_view, name='add_to_cart'),
    path('cart/increase/<int:item_id>/', increase_cart_item_quantity, name='increase_cart_item'),
    path('cart/decrease/<int:item_id>/', decrease_cart_item_quantity, name='decrease_cart_item'),
    path('checkout/', checkout_view, name='checkout'),
    path('order-successful/', order_successful_view, name='order_successful'),
    path('wishlist/', wishlist_view, name='wishlist'),
    path('wishlist/add/<int:product_id>/', add_to_wishlist_view, name='add_to_wishlist'),
    path('wishlist/remove/<int:product_id>/', remove_from_wishlist_view, name='remove_from_wishlist'),
    path('price-alerts/', price_alert_view, name='price_alert_list'),
    path('price-alerts/add/<int:product_id>/', add_price_alert_view, name='add_price_alert'),
    path('price-alerts/remove/<int:alert_id>/', remove_price_alert_view, name='remove_price_alert'),
]
