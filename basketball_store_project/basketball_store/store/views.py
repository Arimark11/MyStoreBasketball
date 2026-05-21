from django.shortcuts import render
from .models import News
from .models import CompanyInfo
from .models import GlossaryTerm
from .models import Employee
from .models import Vacancy
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .forms import ReviewForm
from .models import Review
from .models import PromoCode
from .models import PrivacyPolicy
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from .forms import CustomUserCreationForm, CustomUserChangeForm
from django.contrib.auth import logout
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, Count, Q
from .models import SneakerSize
from .forms import CatalogFilterForm
from django.shortcuts import get_object_or_404, redirect
import requests
import random
from django.contrib import messages
from .models import JobApplication
from .forms import JobApplicationForm
import logging
from statistics import median, mode
from datetime import date
from .models import User, Order, OrderItem, Sneaker, Brand
from django.core.paginator import Paginator



logger = logging.getLogger('store')

class NewsListView(ListView):
    model = News
    template_name = 'news_list.html'
    context_object_name = 'news'
    ordering = ['-created_at']

class NewsDetailView(DetailView):
    model = News
    template_name = 'news_detail.html'
    context_object_name = 'news_item'

def home(request):
    last_news = News.objects.order_by('-created_at').first()
    weather = get_weather()
    basketball_player = get_random_basketball_player()   # ← вызов
    context = {
        'last_news': last_news,
        'weather': weather,
        'basketball_player': basketball_player,
    }
    return render(request, 'home.html', context)

def about(request):
    company = CompanyInfo.objects.first()
    return render(request, 'about.html', {'company': company})

def glossary(request):
    terms = GlossaryTerm.objects.all().order_by('term')
    return render(request, 'glossary.html', {'terms': terms})

def contacts(request):
    employees = Employee.objects.all()
    return render(request, 'contacts.html', {'employees': employees})

def vacancies(request):
    vacancies = Vacancy.objects.all().order_by('-posted_at')
    return render(request, 'vacancies.html', {'vacancies': vacancies})

def custom_logout(request):
    logout(request)
    return redirect('home') 

def reviews_view(request):
    all_reviews = Review.objects.select_related('user').all().order_by('-created_at')
    form = ReviewForm()
    return render(request, 'reviews.html', {'reviews': all_reviews, 'form': form})

@login_required
def delete_review(request, review_id):
    if not (request.user.is_editor or request.user.is_superuser):
        return redirect('reviews')
    review = get_object_or_404(Review, id=review_id)
    review.delete()
    return redirect('reviews')

@login_required
def add_review(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.save()
            return redirect('reviews')
    return redirect('reviews')

def promocodes(request):
    now = timezone.now()
    active = PromoCode.objects.filter(is_active=True, valid_from__lte=now, valid_to__gte=now)
    archive = PromoCode.objects.filter(is_active=False) | PromoCode.objects.filter(valid_to__lt=now)
    return render(request, 'promocodes.html', {'active': active, 'archive': archive})

def privacy(request):
    policy = PrivacyPolicy.objects.first()
    return render(request, 'privacy.html', {'policy': policy})

# Регистрация
class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'register.html'
    success_url = reverse_lazy('login')

# Логин (можно использовать стандартный LoginView с шаблоном)
class CustomLoginView(LoginView):
    template_name = 'login.html'

# Выход
class CustomLogoutView(LogoutView):
    next_page = 'home'

# Личный кабинет (только для залогиненных)
@login_required
def profile(request):
    user = request.user
    orders = Order.objects.filter(user=user).order_by('-created_at')
    return render(request, 'profile.html', {'user': user, 'orders': orders})

# Редактирование профиля
class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = CustomUserChangeForm
    template_name = 'profile_edit.html'
    success_url = reverse_lazy('profile')

    def get_object(self, queryset=None):
        return self.request.user
    
class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'register.html'
    success_url = reverse_lazy('login')

@staff_member_required
def analytics(request):
    # 1. Список клиентов в алфавитном порядке + общая сумма их заказов
    customers = User.objects.annotate(total_spent=Sum('orders__total_amount')).order_by('username')
    
    # 2. Общая выручка магазина (оплаченные заказы)
    total_revenue = Order.objects.filter(status='paid').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    # 3. Статистика по суммам заказов (среднее, мода, медиана)
    order_amounts = list(Order.objects.filter(status='paid').values_list('total_amount', flat=True))
    if order_amounts:
        avg_order = sum(order_amounts) / len(order_amounts)
        try:
            order_mode = mode(order_amounts)
        except:
            order_mode = None
        order_median = median(order_amounts)
    else:
        avg_order = order_mode = order_median = None
    
    # 4. Возраст клиентов (средний и медианный)
    ages = []
    for user in User.objects.filter(birth_date__isnull=False):
        age = user.age if hasattr(user, 'age') else (date.today().year - user.birth_date.year)
        ages.append(age)
    avg_age = sum(ages) / len(ages) if ages else None
    median_age = median(ages) if ages else None
    
    # 5. Самый популярный бренд (по количеству проданных пар)
    brand_sales = Brand.objects.annotate(total_sold=Sum('sneakers__sizes__orderitem__quantity')).order_by('-total_sold')
    top_brand = brand_sales.first()
    
    # 6. Модель, приносящая наибольшую прибыль (считаем price_at_time * quantity по каждому OrderItem)
    profit_by_model = {}
    for item in OrderItem.objects.select_related('sneaker_size__sneaker'):
        sneaker = item.sneaker_size.sneaker
        profit = item.price_at_time * item.quantity
        profit_by_model[sneaker.id] = profit_by_model.get(sneaker.id, 0) + profit
    if profit_by_model:
        top_model_id = max(profit_by_model, key=profit_by_model.get)
        top_model = Sneaker.objects.get(id=top_model_id)
        top_model_profit = profit_by_model[top_model_id]
    else:
        top_model = None
        top_model_profit = 0
    
    context = {
        'customers': customers,
        'total_revenue': total_revenue,
        'avg_order': avg_order,
        'order_mode': order_mode,
        'order_median': order_median,
        'avg_age': avg_age,
        'median_age': median_age,
        'top_brand': top_brand,
        'top_model': top_model,
        'top_model_profit': top_model_profit,
    }
    return render(request, 'analytics.html', context)

def catalog(request):
    sneakers = Sneaker.objects.all()
    form = CatalogFilterForm(request.GET or None)
    
    if form.is_valid():
        brand = form.cleaned_data.get('brand')
        category = form.cleaned_data.get('category')
        season = form.cleaned_data.get('season')
        size = form.cleaned_data.get('size')
        search = form.cleaned_data.get('search')
        sort = form.cleaned_data.get('sort')
        
        if brand:
            sneakers = sneakers.filter(brand=brand)
        if category:
            sneakers = sneakers.filter(category=category)
        if season:
            sneakers = sneakers.filter(season=season)
        if size:
            # фильтр по наличию размера
            sneakers = sneakers.filter(sizes__size__size=size, sizes__stock__gt=0).distinct()
        if search:
            sneakers = sneakers.filter(model_name__icontains=search)
        
        # сортировка
        if sort == 'price_asc':
            sneakers = sneakers.order_by('price')
        elif sort == 'price_desc':
            sneakers = sneakers.order_by('-price')
        elif sort == 'name_asc':
            sneakers = sneakers.order_by('model_name')
        elif sort == 'name_desc':
            sneakers = sneakers.order_by('-model_name')
    
    # Для каждого товара добавим список доступных размеров
    for s in sneakers:
        s.available_sizes = s.sizes.filter(stock__gt=0).select_related('size')
    
    context = {
        'sneakers': sneakers,
        'form': form,
    }
    return render(request, 'catalog.html', context)

@login_required
def cart_add(request):
    if request.method == 'POST':
        sneaker_size_id = request.POST.get('sneaker_size_id')
        quantity = int(request.POST.get('quantity', 1))
        
        # Проверка наличия
        try:
            sneaker_size = SneakerSize.objects.get(id=sneaker_size_id)
            if quantity > sneaker_size.stock:
                messages.error(request, f'Недостаточно товара. Доступно только {sneaker_size.stock} шт.')
                return redirect('catalog')
        except SneakerSize.DoesNotExist:
            messages.error(request, 'Товар не найден.')
            return redirect('catalog')
        
        logger.info(f"User {request.user.username} added {quantity} of sneaker_size {sneaker_size_id} to cart")
        
        cart = request.session.get('cart', {})
        cart[sneaker_size_id] = cart.get(sneaker_size_id, 0) + quantity
        request.session['cart'] = cart
        messages.success(request, 'Товар добавлен в корзину.')
        return redirect('catalog')

def cart_view(request):
    cart = request.session.get('cart', {})
    items = []
    total = 0
    for sz_id, qty in cart.items():
        try:
            sneaker_size = SneakerSize.objects.get(id=sz_id)
            subtotal = sneaker_size.sneaker.price * qty
            total += subtotal
            items.append({
                'sneaker_size': sneaker_size,
                'quantity': qty,
                'subtotal': subtotal,
            })
        except SneakerSize.DoesNotExist:
            continue
    return render(request, 'cart.html', {'items': items, 'total': total})

def cart_remove(request, sneaker_size_id):
    cart = request.session.get('cart', {})
    if str(sneaker_size_id) in cart:
        del cart[str(sneaker_size_id)]
        request.session['cart'] = cart
    return redirect('cart_view')


@login_required
def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.warning(request, 'Ваша корзина пуста.')
        return redirect('cart_view')
    
    # Проверка наличия товаров в нужном количестве
    errors = []
    for sz_id, qty in cart.items():
        try:
            sneaker_size = SneakerSize.objects.get(id=sz_id)
            if sneaker_size.stock < qty:
                errors.append(f"{sneaker_size.sneaker.brand.name} {sneaker_size.sneaker.model_name} (размер {sneaker_size.size.size}) — доступно только {sneaker_size.stock} шт.")
        except SneakerSize.DoesNotExist:
            errors.append(f"Товар с ID {sz_id} не найден.")
    
    if errors:
        for err in errors:
            messages.error(request, err)
        return redirect('cart_view')
    
    # Создаём заказ и уменьшаем остатки
    order = Order.objects.create(user=request.user, total_amount=0, status='pending')
    total = 0
    for sz_id, qty in cart.items():
        sneaker_size = SneakerSize.objects.get(id=sz_id)
        price = sneaker_size.sneaker.price
        OrderItem.objects.create(
            order=order,
            sneaker_size=sneaker_size,
            quantity=qty,
            price_at_time=price
        )
        total += price * qty
        # Уменьшаем остаток
        sneaker_size.stock -= qty
        sneaker_size.save()
    
    order.total_amount = total
    order.save()
    
    logger.info(f"Order {order.id} created by {request.user.username} for total {total}")
    
    # Очищаем корзину
    request.session['cart'] = {}
    messages.success(request, f'Заказ №{order.id} оформлен!')
    return render(request, 'checkout_done.html', {'order': order})

@login_required
def manage_orders(request):
    if not (request.user.is_superuser or request.user.is_manager):
        return redirect('home')  # Доступ только менеджерам/админам
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'manage_orders.html', {'orders': orders})

@login_required
def update_order_status(request, order_id):
    if not (request.user.is_superuser or request.user.is_manager):
        return redirect('home')
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
    return redirect('manage_orders')


def get_weather():
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": 53.9,      # Минск
        "longitude": 27.5667,
        "current_weather": "true",
        "timezone": "Europe/Minsk"
    }
    try:
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        weather = data["current_weather"]
        return {
            "temperature": weather["temperature"],
            "windspeed": weather["windspeed"],
            "city": "Минск"
        }
    except Exception as e:
        logger.error(f"Weather API error: {e}")
        return None

from django.conf import settings
from django.core.cache import cache

def get_random_basketball_player():
    cache_key = 'basketball_player'
    player = cache.get(cache_key)
    if player:
        return player

    api_key = getattr(settings, 'BALLDONTLIE_API_KEY', '')
    if not api_key:
        print("No API key for balldontlie.io")
        return None

    url = "https://api.balldontlie.io/v1/players"
    headers = {"Authorization": api_key}
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            players = data.get('data', [])
            if players:
                player = random.choice(players)
                result = {
                    "first_name": player.get("first_name", ""),
                    "last_name": player.get("last_name", ""),
                    "team": player.get("team", {}).get("full_name", "Unknown"),
                    "position": player.get("position", "Unknown")
                }
                cache.set(cache_key, result, 60*5)  # кэш на 5 минут
                return result
        else:
            print(f"API error: {response.status_code}")
    except Exception as e:
        print(f"Request error: {e}")
    return None

@login_required
def apply_for_vacancy(request, vacancy_id):
    vacancy = get_object_or_404(Vacancy, id=vacancy_id)
    # Проверяем, не подавал ли пользователь уже заявку
    existing_application = JobApplication.objects.filter(user=request.user, vacancy=vacancy).first()
    if existing_application:
        messages.warning(request, 'Вы уже подавали заявку на эту вакансию.')
        return redirect('vacancies')
    
    if request.method == 'POST':
        form = JobApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.vacancy = vacancy
            application.save()
            messages.success(request, 'Ваша заявка успешно отправлена.')
            return redirect('vacancies')
    else:
        form = JobApplicationForm()
    return render(request, 'apply_vacancy.html', {'vacancy': vacancy, 'form': form})

@staff_member_required
def manage_applications(request):
    applications = JobApplication.objects.select_related('user', 'vacancy').all().order_by('-created_at')
    return render(request, 'manage_applications.html', {'applications': applications})

@staff_member_required
def update_application_status(request, application_id):
    application = get_object_or_404(JobApplication, id=application_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(JobApplication.STATUS_CHOICES):
            application.status = new_status
            application.save()

            logger.info(f"Application {application_id} status changed to {new_status} by {request.user.username}")

            if new_status == 'approved':
                user = application.user
                if 'менеджер' in application.vacancy.title.lower():
                    user.is_manager = True
                    user.save()
                if 'работник склада' in application.vacancy.title.lower() or 'сотрудник склада' in application.vacancy.title.lower():
                    user.is_warehouse = True
                    user.save()
                if 'работник сайта' in application.vacancy.title.lower() or 'редактор' in application.vacancy.title.lower():
                    user.is_editor = True
                    user.save()
                # Создаём или обновляем сотрудника
                employee, created = Employee.objects.get_or_create(
                    user=user,
                    defaults={
                        'name': f"{user.first_name} {user.last_name}".strip() or user.username,
                        'position': application.vacancy.title,
                        'phone': user.phone,
                        'email': user.email,
                        'description': f"Принят на вакансию {application.vacancy.title}"
                    }
                )
                if not created:
                    employee.position = application.vacancy.title
                    employee.description = f"Принят на вакансию {application.vacancy.title}"
                    employee.save()
            messages.success(request, f'Статус заявки {application.user.username} изменён.')
    return redirect('manage_applications')


@login_required
def manage_stock(request):
    if not (request.user.is_superuser or request.user.is_warehouse):
        return redirect('home')
    
    sneakers = Sneaker.objects.prefetch_related('sizes__size').all()
    return render(request, 'manage_stock.html', {'sneakers': sneakers})

@login_required
def update_stock(request):
    if not (request.user.is_superuser or request.user.is_warehouse):
        return redirect('home')
    
    if request.method == 'POST':
        # Получаем все пары (sneaker_size_id -> новое значение stock)
        for key, value in request.POST.items():
            if key.startswith('stock_'):
                sneaker_size_id = key.split('_')[1]
                try:
                    new_stock = int(value)
                    sneaker_size = SneakerSize.objects.get(id=sneaker_size_id)
                    sneaker_size.stock = new_stock
                    sneaker_size.save()
                except (ValueError, SneakerSize.DoesNotExist):
                    pass
        messages.success(request, 'Остатки успешно обновлены.')
    return redirect('manage_stock')


def is_editor_or_superuser(user):
    return user.is_authenticated and (user.is_editor or user.is_superuser)

class NewsCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = News
    fields = ['title', 'summary', 'full_text', 'image']
    template_name = 'news_form.html'
    success_url = reverse_lazy('news_list')

    def test_func(self):
        return is_editor_or_superuser(self.request.user)

class NewsUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = News
    fields = ['title', 'summary', 'full_text', 'image']
    template_name = 'news_form.html'
    success_url = reverse_lazy('news_list')

    def test_func(self):
        return is_editor_or_superuser(self.request.user)

class NewsDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = News
    template_name = 'news_confirm_delete.html'
    success_url = reverse_lazy('news_list')

    def test_func(self):
        return is_editor_or_superuser(self.request.user)
    

def sneaker_detail(request, sneaker_id):
    sneaker = get_object_or_404(Sneaker, id=sneaker_id)
    return render(request, 'sneaker_detail.html', {'sneaker': sneaker})


def catalog_paginated(request, page_number=1):
    sneakers_list = Sneaker.objects.all().order_by('id')
    paginator = Paginator(sneakers_list, 6)  # 6 товаров на страницу
    page_obj = paginator.get_page(page_number)
    return render(request, 'catalog_paginated.html', {'page_obj': page_obj})