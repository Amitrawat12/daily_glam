from django.urls import path
from . import views

app_name = 'advice'

urlpatterns = [
    path('', views.beauty_advice_view, name='beauty_advice'),
    path('visual/', views.visual_advice_view, name='visual_advice'),
    path('recommendations/', views.get_ai_recommendations, name='get_ai_recommendations'),
]
