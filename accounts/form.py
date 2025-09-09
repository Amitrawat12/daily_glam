from django import forms
from django.contrib.auth.models import User
from .models import Profile

from django import forms
from django.contrib.auth.models import User
from .models import Profile
from django.core.exceptions import ValidationError

class RegisterForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    phone = forms.CharField(max_length=15)
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")

        return cleaned_data

    def save(self):
        email = self.cleaned_data['email']
        phone = self.cleaned_data['phone']

        # Pre-checks before saving
        if User.objects.filter(email=email).exists():
            raise ValidationError("A user with this email already exists.")
        if Profile.objects.filter(phone=phone).exists():
            raise ValidationError("A user with this phone number already exists.")

        # Safe to create now
        user = User.objects.create_user(
            username=email,
            email=email,
            password=self.cleaned_data['password'],
            first_name=self.cleaned_data['name']
        )

        Profile.objects.create(user=user, phone=phone)
        return user


class LoginForm(forms.Form):
    username = forms.CharField(label="Email or Phone")
    password = forms.CharField(widget=forms.PasswordInput)
