from django.urls import path
from . import views

app_name = 'search'

urlpatterns = [
    path('', views.search_results, name='search_results'),
    path('suggestions/', views.search_suggestions, name='search_suggestions'),
]
