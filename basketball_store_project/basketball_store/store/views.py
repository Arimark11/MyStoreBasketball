from django.shortcuts import render
from .models import User
from .models import News
from .models import CompanyInfo
from .models import GlossaryTerm
from .models import Employee
from .models import Vacancy
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.utils import timezone
from .forms import ReviewForm
from .models import Review
from .models import PromoCode
from .models import PrivacyPolicy
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import Order
from django.contrib.auth import logout
from django.views.generic import ListView, DetailView, CreateView, UpdateView

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
    return render(request, 'home.html', {'last_news': last_news})

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