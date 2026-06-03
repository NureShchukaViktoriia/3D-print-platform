from django import forms
from .models import Order, CartItem, Color
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
        ]

        widgets = {
            'customer_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': "Ім'я"
                }
            ),

            'customer_phone': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Телефон'
                }
            ),
        }

class CartItemForm(forms.ModelForm):
    class Meta:
        model = CartItem
        fields = [
            'material',
            'quality',
            'size',
            'wall_thickness',
            'infill',
            'quantity',
            'color',
        ]

        widgets = {
            'material': forms.Select(attrs={'class': 'form-select'}),
            'quality': forms.Select(attrs={'class': 'form-select'}),
            'size': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'wall_thickness': forms.Select(attrs={'class': 'form-select'}),
            'infill': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'color': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        material_id = kwargs.pop('material_id', None)

        super().__init__(*args, **kwargs)

        if self.data.get('material'):
            material_id = self.data.get('material')
        elif self.instance and self.instance.pk:
            material_id = self.instance.material_id

        if material_id:
            self.fields['color'].queryset = Color.objects.filter(
                materials__id=material_id
            )
        else:
            self.fields['color'].queryset = Color.objects.all()

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