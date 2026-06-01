from django import forms
from .models import Order
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email')

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class OrderForm(forms.ModelForm):

    class Meta:
        model = Order

        fields = [
            'customer_name',
            'customer_phone',
            'material',
            'quality',
            'size',
            'wall_thickness',
            'infill',
            'quantity',
            'color',
        ]

        widgets = {
            'customer_name': forms.TextInput(
                attrs={'class': 'form-control'}
            ),

            'customer_phone': forms.TextInput(
                attrs={'class': 'form-control'}
            ),

            'material': forms.Select(
                attrs={'class': 'form-select'},
                choices=[
                    ('PLA', 'PLA'),
                    ('PETG', 'PETG'),
                    ('ABS', 'ABS'),
                ]
            ),

            'size': forms.NumberInput(
                attrs={'class': 'form-control'}
            ),

            'quality': forms.Select(
                attrs={'class': 'form-select'},
                choices=[
                    (100, '100 мкм'),
                    (200, '200 мкм'),
                    (300, '300 мкм'),
                ]
            ),

            'wall_thickness': forms.Select(
                attrs={'class': 'form-select'},
                choices=[
                    (1, '1 мм'),
                    (2, '2 мм'),
                    (3, '3 мм'),
                ]
            ),

            'infill': forms.Select(
                attrs={'class': 'form-select'},
                choices=[
                    (5, '5%'),
                    (10, '10%'),
                    (25, '25%'),
                    (50, '50%'),
                    (75, '75%'),
                    (100, '100%'),
                ]
            ),

            'color': forms.Select(
                attrs={'class': 'form-select'},
                choices=Order.COLOR_CHOICES
            ),

            'quantity': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'min': 1,
                    'value': 1
                }
            ),
        }


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']

        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Логін"
            }),

            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email'
            }),
        }