# shop/views.py
from typing import Optional
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from .forms import SignUpForm, CheckoutForm
from django.contrib import messages
from django.db.models import Q
from django.urls import reverse
from .models import Product, Cart, CartItem, Category, Order


def product_list(request: HttpRequest, category_id: Optional[int] = None) -> HttpResponse:
    """
    Возвращает список продуктов, возможно фильтрованный по категории и поисковому запросу.

    :param request: HttpRequest объект
    :param category_id: Идентификатор категории для фильтрации (необязательно)
    :return: HttpResponse с отрендеренным шаблоном product_list.html
    """
    categories = Category.objects.all()
    products = Product.objects.all()
    query = request.GET.get('q')

    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )

    if category_id:
        products = products.filter(category_id=category_id)

    return render(request, 'product_list.html',
                  {'products': products, 'categories': categories, 'category_id': category_id, 'query': query})


@login_required
def update_cart(request: HttpRequest) -> HttpResponse:
    """
    Обновляет количество товаров в корзине для текущего пользователя.

    :param request: HttpRequest объект
    :return: HttpResponse перенаправление на страницу корзины
    """
    if request.method == 'POST':
        cart = Cart.objects.get(user=request.user)

        # Обрабатываем каждый товар в корзине
        for item in cart.items.all():
            # Получаем новое количество товара из POST-запроса
            quantity = int(request.POST.get(f'quantity_{item.id}'))
            # Устанавливаем новое количество товара в корзине
            item.quantity = quantity
            item.save()

        # Перенаправляем пользователя обратно на страницу корзины
        return redirect('cart_detail')

    # Если метод запроса не POST, перенаправляем на домашнюю страницу
    return redirect('home')


@login_required
def cart_detail(request: HttpRequest) -> HttpResponse:
    """
    Возвращает детали корзины для текущего пользователя.

    :param request: HttpRequest объект
    :return: HttpResponse с отрендеренным шаблоном cart_detail.html
    """
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, 'cart_detail.html', {'cart': cart})


@login_required
def add_to_cart(request: HttpRequest, product_id: int) -> HttpResponse:
    """
    Добавляет товар в корзину текущего пользователя.

    :param request: HttpRequest объект
    :param product_id: Идентификатор добавляемого товара
    :return: HttpResponse перенаправление на страницу корзины
    """
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('cart_detail')


@login_required
def remove_from_cart(request: HttpRequest, product_id: int) -> HttpResponse:
    """
    Удаляет товар из корзины текущего пользователя.

    :param request: HttpRequest объект
    :param product_id: Идентификатор удаляемого товара
    :return: HttpResponse перенаправление на страницу корзины
    """
    cart = Cart.objects.get(user=request.user)
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(cart=cart, product=product)
    cart_item.delete()
    return redirect('cart_detail')


@login_required
def checkout(request: HttpRequest) -> HttpResponse:
    """
    Оформляет заказ для текущего пользователя.

    :param request: HttpRequest объект
    :return: HttpResponse с отрендеренным шаблоном checkout.html или перенаправление на страницу успеха заказа
    """
    cart = Cart.objects.get(user=request.user)

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            delivery_address = form.cleaned_data['delivery_address']
            phone_number = form.cleaned_data['phone_number']
            payment_option = form.cleaned_data['payment_option']

            # Создание нового заказа
            order = Order.objects.create(
                user=request.user,
                total_cost=cart.get_total_cost()
            )
            order.items.set(cart.items.all())  # Добавляем товары из корзины в заказ

            # # Очистка корзины
            # cart.items.clear()

            return redirect(
                reverse('order_success', args=[order.id]))  # Перенаправление на страницу успешного оформления заказа
    else:
        form = CheckoutForm()

    return render(request, 'checkout.html', {'form': form})


def order_success(request: HttpRequest, order_id: int) -> HttpResponse:
    """
    Отображает страницу успешного оформления заказа.

    :param request: HttpRequest объект
    :param order_id: Идентификатор заказа
    :return: HttpResponse с отрендеренным шаблоном order_success.html
    """
    order = Order.objects.get(id=order_id)  # Получаем объект заказа по его ID
    return render(request, 'order_success.html', {'order': order})


def product_detail(request: HttpRequest, pk: int) -> HttpResponse:
    """
    Отображает детали конкретного продукта.

    :param request: HttpRequest объект
    :param pk: Идентификатор продукта
    :return: HttpResponse с отрендеренным шаблоном product_detail.html
    """
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'product_detail.html', {'product': product})


def home(request: HttpRequest) -> HttpResponse:
    """
    Отображает домашнюю страницу.

    :param request: HttpRequest объект
    :return: HttpResponse с отрендеренным шаблоном home.html
    """
    return render(request, 'home.html')


@login_required
def profile(request: HttpRequest) -> HttpResponse:
    """
    Отображает профиль текущего пользователя.

    :param request: HttpRequest объект
    :return: HttpResponse с отрендеренным шаблоном profile.html
    """
    return render(request, 'profile.html', {'user': request.user})


@login_required
def change_password(request: HttpRequest) -> HttpResponse:
    """
    Позволяет пользователю сменить пароль.

    :param request: HttpRequest объект
    :return: HttpResponse с отрендеренным шаблоном change_password.html
    """
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # обновляем сессию пользователя, чтобы он не был разлогинен
            messages.success(request, 'Ваш пароль успешно изменен!')
            return redirect('profile')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change_password.html', {'form': form})


@login_required
def order_history(request: HttpRequest) -> HttpResponse:
    """
    Отображает историю заказов текущего пользователя.

    :param request: HttpRequest объект
    :return: HttpResponse с отрендеренным шаблоном order_history.html
    """
    orders = Order.objects.filter(user=request.user)
    return render(request, 'order_history.html', {'orders': orders})


def signup(request: HttpRequest) -> HttpResponse:
    """
    Регистрирует нового пользователя.

    :param request: HttpRequest объект
    :return: HttpResponse с отрендеренным шаблоном signup.html
    """
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


def login_view(request: HttpRequest) -> HttpResponse:
    """
    Авторизует пользователя.

    :param request: HttpRequest объект
    :return: HttpResponse с отрендеренным шаблоном login.html
    """
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def logout_view(request: HttpRequest) -> HttpResponse:
    """
    Выход пользователя из системы.

    :param request: HttpRequest объект
    :return: HttpResponse перенаправление на домашнюю страницу
    """
    logout(request)
    return redirect('home')
