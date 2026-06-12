from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('catalog/', views.catalog, name='catalog'),
    path('model/<int:model_id>/', views.model_detail, name='model_detail'),
    path('order/<int:model_id>/', views.order_create, name='order_create'),
    path('order-success/<int:order_id>/', views.order_success, name='order_success'),
    path('register/', views.register_view, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='main/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('favorites/', views.favorites_view, name='favorites'),
    path('favorite/<int:model_id>/', views.toggle_favorite, name='toggle_favorite'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('info/', views.info, name='info'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:model_id>/', views.cart_add, name='cart_add'),
    path('cart/item/<int:item_id>/edit/', views.cart_item_edit, name='cart_item_edit'),
    path('cart/item/<int:item_id>/delete/', views.cart_item_delete, name='cart_item_delete'),
    path('cart/order/', views.order_create_from_cart, name='order_create_from_cart'),
    path('ajax/colors/', views.get_colors_by_material, name='get_colors_by_material'),
    path('ajax/calculate-cart-price/', views.calculate_cart_price, name='calculate_cart_price'),
]