from django.contrib import admin
from .models import Category, Material, Model3D, ModelImage, Favorite, Order, PrintQuality, MaterialPrice, Color

admin.site.register(Category)
admin.site.register(Material)
admin.site.register(Model3D)
admin.site.register(ModelImage)
admin.site.register(Favorite)
admin.site.register(Order)
admin.site.register(PrintQuality)
admin.site.register(MaterialPrice)
admin.site.register(Color)