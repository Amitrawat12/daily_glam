from django.urls import path
from . import views

app_name = 'compare'

urlpatterns = [
    path('', views.compare_home, name='compare_home'),
    path('add/', views.add_to_compare, name='add_to_compare'),
    path('page/', views.compare_page_view, name='compare_page'),
    path('remove/<int:product_id>/', views.remove_from_compare, name='remove_from_compare'),
    path('clear/', views.clear_compare, name='clear_compare'),
    path('product/<str:product_id>/', views.product_detail_view, name='product_detail'),
    path('category/<str:category_name>/', views.category_view, name='compare_category'),
]
