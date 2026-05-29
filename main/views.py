from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm
from .utils import calculate_order_price
from .models import Model3D, Order, Category, Material
from .forms import OrderForm

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
    return render(request, 'main/home.html')


def catalog(request):
    models = Model3D.objects.all()
    categories = Category.objects.all()
    materials = Material.objects.all()

    query = request.GET.get('q')
    category_id = request.GET.get('category')
    material_id = request.GET.get('material')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    if query:
        models = models.filter(name__icontains=query)

    if category_id:
        models = models.filter(category_id=category_id)

    if material_id:
        models = models.filter(recommended_material_id=material_id)

    if min_price:
        models = models.filter(base_price__gte=min_price)

    if max_price:
        models = models.filter(base_price__lte=max_price)

    sort = request.GET.get('sort')

    if sort == 'price_asc':
        models = models.order_by('base_price')
    elif sort == 'price_desc':
        models = models.order_by('-base_price')
    elif sort == 'name':
        models = models.order_by('name')
    elif sort == 'newest':
        models = models.order_by('-created_at')

    return render(
        request,
        'main/catalog.html',
        {
            'models': models,
            'categories': categories,
            'materials': materials,
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
            order.total_price = calculate_order_price(order, model)
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

    return render(request, 'main/profile.html', {
        'orders': orders
    })