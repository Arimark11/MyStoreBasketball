from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from datetime import date
import pytz
from django.core.validators import ValidationError

#Кастомный пользователь
class User(AbstractUser):
    phone_regex = RegexValidator(
        regex=r'^\+375 \(29\) \d{3}-\d{2}-\d{2}$',
        message="Номер телефона должен быть в формате +375 (29) XXX-XX-XX"
    )
    phone = models.CharField(validators=[phone_regex], max_length=20, unique=True)
    birth_date = models.DateField(null=True, blank=True)
    is_manager = models.BooleanField(default=False, verbose_name='Статус менеджера')
    is_warehouse = models.BooleanField(default=False, verbose_name='Сотрудник склада')
    is_editor = models.BooleanField(default=False, verbose_name='Редактор сайта')
    timezone = models.CharField(
        max_length=50,
        choices=[(tz, tz) for tz in pytz.common_timezones],
        default='UTC',
        verbose_name='Часовой пояс'
    )

    @property
    def age(self):
        if not self.birth_date:
            return None
        today = date.today()
        return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))

    def save(self, *args, **kwargs):
        if self.birth_date and self.age < 18:
            raise ValueError("Возраст должен быть 18+")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username

#Бренд
class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    country = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='brands/', blank=True, null=True)

    def __str__(self):
        return self.name

#Категория
class Category(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

#Кроссовки
class Sneaker(models.Model):
    SEASON_CHOICES = [
        ('summer', 'Лето'),
        ('winter', 'Зима'),
        ('all_season', 'Всесезонные'),
    ]
    model_name = models.CharField(max_length=200)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='sneakers')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='sneakers')
    season = models.CharField(max_length=20, choices=SEASON_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    description = models.TextField()
    image = models.ImageField(upload_to='sneakers/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.brand.name} {self.model_name}"

#Размер
class Size(models.Model):
    size = models.PositiveSmallIntegerField(unique=True)

    def __str__(self):
        return str(self.size)

#Размер-Кроссовки (промежуточная для ManyToMany с остатком)
class SneakerSize(models.Model):
    sneaker = models.ForeignKey(Sneaker, on_delete=models.CASCADE, related_name='sizes')
    size = models.ForeignKey(Size, on_delete=models.CASCADE, related_name='sneakers')
    stock = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('sneaker', 'size')

    def __str__(self):
        return f"{self.sneaker} - размер {self.size} (остаток: {self.stock})"

#Промокод
class PromoCode(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_percent = models.PositiveSmallIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.code

#Заказ
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает оплаты'),
        ('paid', 'Оплачен'),
        ('shipped', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменён'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    promo = models.ForeignKey(PromoCode, on_delete=models.SET_NULL, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Заказ {self.id} от {self.user.username}"

#Товар в заказе
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    sneaker_size = models.ForeignKey(SneakerSize, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price_at_time = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.sneaker_size.sneaker} x{self.quantity}"

#Модели для обязательных страниц

class News(models.Model):
    title = models.CharField(max_length=200)
    summary = models.CharField(max_length=300)
    full_text = models.TextField()
    image = models.ImageField(upload_to='news/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class GlossaryTerm(models.Model):
    term = models.CharField(max_length=100)
    definition = models.TextField()
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.term

class Employee(models.Model):
    photo = models.ImageField(upload_to='employees/', blank=True, null=True)
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Vacancy(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField()
    posted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
class JobApplication(models.Model):
    STATUS_CHOICES = [
        ('pending', 'На рассмотрении'),
        ('approved', 'Одобрено'),
        ('rejected', 'Отклонено'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_applications')
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE, related_name='applications')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(blank=True, verbose_name='Комментарий к заявке')

    class Meta:
        unique_together = ('user', 'vacancy')  # чтобы один пользователь не мог подать повторно на ту же вакансию

    def __str__(self):
        return f"{self.user.username} -> {self.vacancy.title} ({self.status})"

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Отзыв от {self.user.username} - {self.rating}★"

class CompanyInfo(models.Model):
    name = models.CharField(max_length=200, default="О компании")
    history = models.TextField(blank=True)
    requisites = models.TextField(blank=True)
    logo = models.ImageField(upload_to='company/', blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name

class PrivacyPolicy(models.Model):
    content = models.TextField(default="Содержимое страницы политики конфиденциальности")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Политика конфиденциальности"
    
class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='employee_profile')
    photo = models.ImageField(upload_to='employees/', blank=True, null=True)
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name
