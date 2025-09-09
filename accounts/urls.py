from django.urls import path
from .views import profile_view, login_view, register_view, custom_logout_view

app_name = 'accounts'

urlpatterns = [
    path('profile/', profile_view, name='profile'),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', custom_logout_view, name='logout'),
]
