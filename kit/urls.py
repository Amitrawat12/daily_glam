from django.urls import path
from . import views

app_name = 'kit'

urlpatterns = [
    path('', views.kit_home, name='kit_home'),
    path('category/<str:category_name>/', views.category_view, name='kit_category'),
    path('add-to-kit/', views.add_to_kit, name='add_to_kit'),
    path('view/', views.view_kit, name='kit_view'),
    path('clear/', views.clear_kit, name='kit_clear'),
    path('remove/<int:offer_id>/', views.remove_from_kit, name='kit_remove'),
    path('increase/<int:offer_id>/', views.increase_kit_item_quantity, name='increase_kit_item'),
    path('decrease/<int:offer_id>/', views.decrease_kit_item_quantity, name='decrease_kit_item'),
    path('add-to-cart/', views.add_kit_to_cart, name='kit_add_to_cart'),
]
