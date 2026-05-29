from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Назва категорії")
    description = models.TextField(blank=True, null=True, verbose_name="Опис")

    def __str__(self):
        return self.name


class Material(models.Model):
    name = models.CharField(max_length=100, verbose_name="Назва матеріалу")
    description = models.TextField(blank=True, null=True, verbose_name="Опис")
    price_per_gram = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name="Ціна за грам"
    )

    def __str__(self):
        return self.name


class Model3D(models.Model):
    name = models.CharField(
        max_length=150,
        verbose_name="Назва моделі"
    )

    description = models.TextField(
        verbose_name="Опис"
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="models",
        verbose_name="Категорія"
    )

    recommended_material = models.ForeignKey(
        Material,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Рекомендований матеріал"
    )

    recommended_size = models.CharField(
        max_length=100,
        verbose_name="Рекомендований розмір"
    )

    recommended_layer_height = models.PositiveIntegerField(
        choices=[
            (100, '100 мкм'),
            (200, '200 мкм'),
            (300, '300 мкм'),
        ],
        verbose_name="Рекомендована висота шару"
    )

    recommended_wall_thickness = models.PositiveIntegerField(
        choices=[
            (1, '1 мм'),
            (2, '2 мм'),
            (3, '3 мм'),
        ],
        verbose_name="Рекомендована товщина стінок"
    )

    recommended_infill = models.PositiveIntegerField(
        choices=[
            (5, '5%'),
            (10, '10%'),
            (25, '25%'),
            (50, '50%'),
            (75, '75%'),
            (100, '100%'),
        ],
        verbose_name="Рекомендоване заповнення"
    )

    base_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Базова ціна"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name


class ModelImage(models.Model):
    model = models.ForeignKey(
        Model3D,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="Модель"
    )

    image = models.ImageField(
        upload_to="models/",
        verbose_name="Зображення"
    )

    is_main = models.BooleanField(
        default=False,
        verbose_name="Головне зображення"
    )

    def __str__(self):
        return f"Зображення для {self.model.name}"


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Користувач"
    )

    model = models.ForeignKey(
        Model3D,
        on_delete=models.CASCADE,
        verbose_name="Модель"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.model.name}"
    

class Order(models.Model):

    STATUS_CHOICES = [
        ('new', 'Нове'),
        ('processing', 'В обробці'),
        ('printing', 'Друкується'),
        ('completed', 'Завершено'),
    ]

    model = models.ForeignKey(
        Model3D,
        on_delete=models.CASCADE,
        verbose_name="Модель"
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    customer_name = models.CharField(
        max_length=100,
        verbose_name="Ім'я"
    )

    customer_phone = models.CharField(
        max_length=20,
        verbose_name="Телефон"
    )

    material = models.CharField(
        max_length=50,
        verbose_name="Матеріал"
    )

    size = models.PositiveIntegerField(
        verbose_name="Розмір"
    )

    layer_height = models.PositiveIntegerField(
        verbose_name="Висота шару"
    )

    wall_thickness = models.PositiveIntegerField(
        verbose_name="Товщина стінок"
    )

    infill = models.PositiveIntegerField(
        verbose_name="Заповнення"
    )

    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name="Кількість"
    )

    COLOR_CHOICES = [
        ('white', 'Білий'),
        ('black', 'Чорний'),
        ('gray', 'Сірий'),
        ('red', 'Червоний'),
        ('blue', 'Синій'),
        ('green', 'Зелений'),
    ]

    color = models.CharField(
        max_length=20,
        choices=COLOR_CHOICES,
        default='white',
        verbose_name="Колір"
    )

    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Замовлення #{self.id}"