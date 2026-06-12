from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from .forms import RegisterForm
from .utils import calculate_print_price
from .models import Model3D, Order, OrderItem, Cart, CartItem, Category, Material, Favorite, Color, PrintQuality
from .forms import OrderForm, CartItemForm
from django.contrib import messages
from .forms import UserProfileForm
from django.http import JsonResponse

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = RegisterForm()

    return render(request, 'main/register.html', {'form': form})


def home(request):
    featured_models = Model3D.objects.all()[:6]

    return render(request, 'main/home.html', {
        'featured_models': featured_models,
    })


def catalog(request):
    models = Model3D.objects.all()
    categories = Category.objects.all()
    materials = Material.objects.all()

    query = request.GET.get('q')
    category_id = request.GET.get('category')
    material_id = request.GET.get('material')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    sort = request.GET.get('sort')

    if query:
        models = models.filter(name__icontains=query)

    if category_id:
        models = models.filter(category_id=category_id)

    if material_id:
        models = models.filter(recommended_material_id=material_id)

    models_with_prices = []

    for model in models:
        price_data = calculate_print_price(
            base_weight=model.base_weight,
            complexity=model.complexity,
            supports_required=model.supports_required,
            recommended_wall_thickness=model.recommended_wall_thickness,
            size=model.recommended_size,
            base_size=model.base_size,
            infill=model.recommended_infill,
            wall_thickness=model.recommended_wall_thickness,
            material=model.recommended_material,
            quality=model.recommended_quality,
            quantity=1
        )

        models_with_prices.append((model, price_data['price']))

    if min_price:
        models_with_prices = [
            item for item in models_with_prices
            if item[1] >= float(min_price)
        ]

    if max_price:
        models_with_prices = [
            item for item in models_with_prices
            if item[1] <= float(max_price)
        ]

    if sort == 'price_asc':
        models_with_prices.sort(key=lambda item: item[1])
    elif sort == 'price_desc':
        models_with_prices.sort(key=lambda item: item[1], reverse=True)
    elif sort == 'name':
        models_with_prices.sort(key=lambda item: item[0].name.lower())
    elif sort == 'newest':
        models_with_prices.sort(key=lambda item: item[0].created_at, reverse=True)

    models_list = [item[0] for item in models_with_prices]

    favorite_ids = []

    if request.user.is_authenticated:
        favorite_ids = Favorite.objects.filter(
            user=request.user
        ).values_list('model_id', flat=True)

    return render(
        request,
        'main/catalog.html',
        {
            'models': models_list,
            'categories': categories,
            'materials': materials,
            'favorite_ids': favorite_ids,
            'selected_category': category_id,
            'selected_material': material_id,
            'min_price': min_price,
            'max_price': max_price,
            'query': query,
            'sort': sort,
        }
    )


def model_detail(request, model_id):
    model = get_object_or_404(Model3D, id=model_id)

    return render(
        request,
        'main/model_detail.html',
        {'model': model}
    )


def order_create(request, model_id):
    model = get_object_or_404(Model3D, id=model_id)

    if request.method == 'POST':
        form = OrderForm(request.POST)

        if form.is_valid():
            order = form.save(commit=False)

            if request.user.is_authenticated:
                order.user = request.user

            order.model = model
            order.save()

            return redirect('order_success', order_id=order.id)
    else:
        form = OrderForm()

    return render(
        request,
        'main/order_create.html',
        {
            'model': model,
            'form': form
        }
    )


def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    return render(
        request,
        'main/order_success.html',
        {'order': order}
    )

@login_required
def profile_view(request):
    orders = Order.objects.filter(
        user=request.user
    ).order_by('-created_at')

    favorites = Favorite.objects.filter(
        user=request.user
    ).select_related('model').order_by('-created_at')

    return render(request, 'main/profile.html', {
        'orders': orders,
        'favorites': favorites
    })

@login_required
def toggle_favorite(request, model_id):
    model = get_object_or_404(Model3D, id=model_id)

    favorite, created = Favorite.objects.get_or_create(
        user=request.user,
        model=model
    )

    if not created:
        favorite.delete()

    return redirect(request.META.get('HTTP_REFERER', 'catalog'))

@login_required
def favorites_view(request):
    favorites = Favorite.objects.filter(
        user=request.user
    ).select_related('model').order_by('-created_at')

    return render(request, 'main/favorites.html', {
        'favorites': favorites
    })

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)

        if form.is_valid():
            form.save()
            messages.success(request, 'Профіль успішно оновлено.')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)

    return render(request, 'main/edit_profile.html', {
        'form': form
    })

def info(request):
    return render(request, 'main/info.html')

@property
def recommended_price(self):

    if not self.recommended_material:
        return 0

    if not self.recommended_quality:
        return 0

    result = calculate_print_price(
        base_weight=self.base_weight,
        complexity=self.complexity,
        recommended_wall_thickness=self.recommended_wall_thickness,
        size=self.recommended_size,
        base_size=self.recommended_size,
        infill=self.recommended_infill,
        wall_thickness=self.recommended_wall_thickness,
        material=self.recommended_material,
        quality=self.recommended_quality,
        quantity=1
    )

    return result["price"]


@login_required
def cart_detail(request):
    cart, created = Cart.objects.get_or_create(user=request.user)

    return render(request, 'main/cart_detail.html', {
        'cart': cart,
        'items': cart.items.all(),
        'total_price': cart.get_total_price()
    })


@login_required
def cart_add(request, model_id):
    model = get_object_or_404(Model3D, id=model_id)
    cart, created = Cart.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = CartItemForm(request.POST, initial={'model': model})

        if form.is_valid():
            item = form.save(commit=False)
            item.cart = cart
            item.model = model
            item.save()

            return redirect('cart_detail')
    else:
        form = CartItemForm(
            material_id=model.recommended_material_id,
            initial={
                'material': model.recommended_material,
                'quality': model.recommended_quality,
                'size': model.recommended_size,
                'wall_thickness': model.recommended_wall_thickness,
                'infill': model.recommended_infill,
                'quantity': 1,
            }
        )

    return render(request, 'main/cart_add.html', {
        'form': form,
        'model': model
    })


@login_required
def cart_item_edit(request, item_id):
    item = get_object_or_404(
        CartItem,
        id=item_id,
        cart__user=request.user
    )

    if request.method == 'POST':
        form = CartItemForm(request.POST, instance=item)

        if form.is_valid():
            form.save()
            return redirect('cart_detail')
    else:
        form = CartItemForm(instance=item)

    return render(request, 'main/cart_item_edit.html', {
        'form': form,
        'item': item,
    })


@login_required
def cart_item_delete(request, item_id):
    item = get_object_or_404(
        CartItem,
        id=item_id,
        cart__user=request.user
    )

    item.delete()
    return redirect('cart_detail')


@login_required
def order_create_from_cart(request):
    cart = get_object_or_404(Cart, user=request.user)
    items = cart.items.all()

    if not items.exists():
        return redirect('cart_detail')

    initial_data = {
        'customer_name': request.user.get_full_name() or request.user.username,
        'customer_phone': getattr(request.user, 'phone', ''),
    }

    if request.method == 'POST':
        form = OrderForm(request.POST)

        if form.is_valid():
            first_item = items.first()

            order = form.save(commit=False)
            order.user = request.user

            # Дані з першої позиції кошика, якщо ці поля ще є в Order
            order.model = first_item.model
            order.material = first_item.material
            order.quality = first_item.quality
            order.size = first_item.size
            order.wall_thickness = first_item.wall_thickness
            order.infill = first_item.infill
            order.quantity = first_item.quantity
            order.color = first_item.color

            order.payment_info = "Оплата при отриманні замовлення на пошті"
            order.total_price = cart.get_total_price()

            order.save()

            for item in items:
                OrderItem.objects.create(
                    order=order,
                    model=item.model,
                    material=item.material,
                    quality=item.quality,
                    size=item.size,
                    wall_thickness=item.wall_thickness,
                    infill=item.infill,
                    quantity=item.quantity,
                    color=item.color,
                    estimated_weight=item.estimated_weight,
                    total_price=item.total_price
                )

            items.delete()

            return redirect('order_success', order_id=order.id)

    else:
        form = OrderForm(initial=initial_data)

    return render(request, 'main/order_create_from_cart.html', {
        'form': form,
        'items': items,
        'total_price': cart.get_total_price()
    })

@login_required
def get_colors_by_material(request):
    material_id = request.GET.get('material_id')

    colors = Color.objects.filter(materials__id=material_id).distinct()

    data = [
        {
            'id': color.id,
            'name': color.name
        }
        for color in colors
    ]

    return JsonResponse({'colors': data})

@login_required
def calculate_cart_price(request):
    model_id = request.GET.get('model_id')
    material_id = request.GET.get('material_id')
    quality_id = request.GET.get('quality_id')
    size = request.GET.get('size')
    wall_thickness = request.GET.get('wall_thickness')
    infill = request.GET.get('infill')
    quantity = request.GET.get('quantity')

    try:
        model = Model3D.objects.get(id=model_id)
        material = Material.objects.get(id=material_id)
        quality = PrintQuality.objects.get(id=quality_id)

        result = calculate_print_price(
            base_weight=model.base_weight,
            complexity=model.complexity,
            supports_required=model.supports_required,
            recommended_wall_thickness=model.recommended_wall_thickness,
            size=int(size),
            base_size=model.base_size,
            infill=int(infill),
            wall_thickness=int(wall_thickness),
            material=material,
            quality=quality,
            quantity=int(quantity)
        )

        return JsonResponse({
            'price': result['price'],
            'weight': result['weight']
        })

    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=400)