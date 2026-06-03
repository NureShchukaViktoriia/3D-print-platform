from django.db import models
from django.contrib.auth.models import User
from .utils import calculate_print_price


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Назва категорії")
    description = models.TextField(blank=True, null=True, verbose_name="Опис")

    def __str__(self):
        return self.name


class Material(models.Model):
    name = models.CharField(max_length=100, verbose_name="Назва матеріалу")
    description = models.TextField(blank=True, null=True, verbose_name="Опис")

    def __str__(self):
        return self.name

class Color(models.Model):
    name = models.CharField(
        max_length=50,
        verbose_name="Назва кольору"
    )

    code = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Код кольору"
    )

    materials = models.ManyToManyField(
        Material,
        related_name="colors",
        verbose_name="Доступний для матеріалів"
    )

    def __str__(self):
        return self.name

class PrintQuality(models.Model):
    name = models.CharField(max_length=100, verbose_name="Назва якості")
    layer_height = models.PositiveIntegerField(
        choices=[
            (100, '100 мкм'),
            (200, '200 мкм'),
            (300, '300 мкм'),
        ],
        verbose_name="Висота шару"
    )

    def __str__(self):
        return f"{self.name} ({self.layer_height} мкм)"


class MaterialPrice(models.Model):
    material = models.ForeignKey(
        Material,
        on_delete=models.CASCADE,
        related_name="prices",
        verbose_name="Матеріал"
    )

    quality = models.ForeignKey(
        PrintQuality,
        on_delete=models.CASCADE,
        related_name="material_prices",
        verbose_name="Якість друку"
    )

    price_per_gram = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name="Ціна за грам"
    )

    class Meta:
        unique_together = ("material", "quality")
        verbose_name = "Ціна матеріалу"
        verbose_name_plural = "Ціни матеріалів"

    def __str__(self):
        return f"{self.material} - {self.quality}: {self.price_per_gram} грн/г"


class Model3D(models.Model):
    name = models.CharField(max_length=150, verbose_name="Назва моделі")
    description = models.TextField(verbose_name="Опис")

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

    recommended_size = models.PositiveIntegerField(
        default=10,
        verbose_name="Рекомендований розмір, см"
    )

    base_size = models.PositiveIntegerField(
        default=10,
        verbose_name="Базовий розмір моделі, см"
    )

    recommended_quality = models.ForeignKey(
        PrintQuality,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Рекомендована якість друку"
    )

    recommended_wall_thickness = models.PositiveIntegerField(
        choices=[
            (1, '1 мм'),
            (2, '2 мм'),
            (3, '3 мм'),
        ],
        default=2,
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

    supports_required = models.BooleanField(
        default=False,
        verbose_name="Потребує підтримок"
    )

    base_weight = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=50,
        verbose_name="Базова вага, г"
    )

    complexity = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=1.00,
        verbose_name="Коефіцієнт складності"
    )


    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    @property
    def recommended_price(self):

        if not self.recommended_material or not self.recommended_quality:
            return 0

        result = calculate_print_price(
            base_weight=self.base_weight,
            complexity=self.complexity,
            supports_required=self.supports_required,
            recommended_wall_thickness=self.recommended_wall_thickness,
            size=self.recommended_size,
            base_size=self.base_size,
            infill=self.recommended_infill,
            wall_thickness=self.recommended_wall_thickness,
            material=self.recommended_material,
            quality=self.recommended_quality,
            quantity=1
        )

        return result["price"]


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
    

class Order(models.Model):

    STATUS_CHOICES = [
        ('new', 'Нове'),
        ('processing', 'В обробці'),
        ('printing', 'Друкується'),
        ('completed', 'Завершено'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Користувач"
    )

    customer_name = models.CharField(
        max_length=100,
        verbose_name="Ім'я"
    )

    customer_phone = models.CharField(
        max_length=20,
        verbose_name="Телефон"
    )

    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Загальна ціна"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
        verbose_name="Статус"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата створення"
    )

    def __str__(self):
        return f"Замовлення #{self.id}"
    
class Cart(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name='Користувач'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def get_total_price(self):
        return sum(item.total_price for item in self.items.all())

    def __str__(self):
        return f"Кошик {self.user.username}"


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Кошик'
    )

    model = models.ForeignKey(
        Model3D,
        on_delete=models.CASCADE,
        verbose_name='Модель'
    )

    material = models.ForeignKey(
        Material,
        on_delete=models.PROTECT,
        verbose_name='Матеріал'
    )

    quality = models.ForeignKey(
        PrintQuality,
        on_delete=models.PROTECT,
        verbose_name='Якість друку'
    )

    size = models.PositiveIntegerField(verbose_name='Розмір, см')

    wall_thickness = models.PositiveIntegerField(
        choices=[
            (1, '1 мм'),
            (2, '2 мм'),
            (3, '3 мм'),
        ],
        default=2,
        verbose_name='Товщина стінок'
    )

    infill = models.PositiveIntegerField(verbose_name='Заповнення, %')

    quantity = models.PositiveIntegerField(default=1, verbose_name='Кількість')
    
    color = models.ForeignKey(
        Color,
        on_delete=models.PROTECT,
        verbose_name="Колір"
    )

    estimated_weight = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0
    )

    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    def calculate_price(self):
        result = calculate_print_price(
            base_weight=self.model.base_weight,
            complexity=self.model.complexity,
            supports_required=self.model.supports_required,
            recommended_wall_thickness=self.model.recommended_wall_thickness,
            size=self.size,
            base_size=self.model.base_size,
            infill=self.infill,
            wall_thickness=self.wall_thickness,
            material=self.material,
            quality=self.quality,
            quantity=self.quantity
        )

        self.estimated_weight = result["weight"]
        self.total_price = result["price"]

    def save(self, *args, **kwargs):
        self.calculate_price()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.model.name} x {self.quantity}"


class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Замовлення'
    )

    model = models.ForeignKey(
        Model3D,
        on_delete=models.CASCADE,
        verbose_name="Модель"
    )

    material = models.ForeignKey(
        Material,
        on_delete=models.PROTECT,
        verbose_name="Матеріал"
    )

    quality = models.ForeignKey(
        PrintQuality,
        on_delete=models.PROTECT,
        verbose_name="Якість друку"
    )

    size = models.PositiveIntegerField(
        verbose_name="Розмір, см"
    )

    wall_thickness = models.PositiveIntegerField(
        choices=[
            (1, '1 мм'),
            (2, '2 мм'),
            (3, '3 мм'),
        ],
        default=2,
        verbose_name="Товщина стінок"
    )

    infill = models.PositiveIntegerField(
        verbose_name="Заповнення, %"
    )

    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name="Кількість"
    )

    color = models.ForeignKey(
        Color,
        on_delete=models.PROTECT,
        verbose_name="Колір"
    )
    
    estimated_weight = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        verbose_name="Орієнтовна вага, г"
    )

    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Ціна позиції"
    )

    def __str__(self):
        return f"{self.model.name} x {self.quantity}"

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

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата додавання"
    )

    class Meta:
        unique_together = ('user', 'model')
        verbose_name = "Улюблена модель"
        verbose_name_plural = "Улюблені моделі"

    def __str__(self):
        return f"{self.user.username} - {self.model.name}"