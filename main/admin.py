from django.contrib import admin
from .models import Category, Material, Model3D, ModelImage, Favorite, Order


admin.site.register(Category)
admin.site.register(Material)
admin.site.register(Model3D)
admin.site.register(ModelImage)
admin.site.register(Favorite)
admin.site.register(Order)