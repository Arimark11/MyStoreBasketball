from django.contrib import admin
from .models import (
    User, Brand, Category, Sneaker, Size, SneakerSize, PromoCode,
    Order, OrderItem, News, GlossaryTerm, Employee, Vacancy, Review,
    CompanyInfo, PrivacyPolicy
)

class SneakerSizeInline(admin.TabularInline):
    model = SneakerSize
    extra = 1

@admin.register(Sneaker)
class SneakerAdmin(admin.ModelAdmin):
    list_display = ('model_name', 'brand', 'category', 'price', 'season')
    list_filter = ('brand', 'category', 'season')
    search_fields = ('model_name', 'brand__name')
    inlines = [SneakerSizeInline]

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'country')
    search_fields = ('name',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ('size',)

@admin.register(SneakerSize)
class SneakerSizeAdmin(admin.ModelAdmin):
    list_display = ('sneaker', 'size', 'stock')
    list_filter = ('sneaker__brand', 'size')

@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_percent', 'valid_from', 'valid_to', 'is_active')
    list_filter = ('is_active',)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total_amount', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username',)
    inlines = [OrderItemInline]

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'sneaker_size', 'quantity', 'price_at_time')

# Обязательные страницы
@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    search_fields = ('title',)

@admin.register(GlossaryTerm)
class GlossaryTermAdmin(admin.ModelAdmin):
    list_display = ('term', 'added_at')
    search_fields = ('term',)

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'phone', 'email')
    search_fields = ('name',)

@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ('title', 'posted_at')
    search_fields = ('title',)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')

@admin.register(CompanyInfo)
class CompanyInfoAdmin(admin.ModelAdmin):
    # ограничиваем, чтобы была только одна запись
    def has_add_permission(self, request):
        if CompanyInfo.objects.exists():
            return False
        return True

@admin.register(PrivacyPolicy)
class PrivacyPolicyAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        if PrivacyPolicy.objects.exists():
            return False
        return True

# Регистрация кастомного пользователя
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'phone', 'birth_date', 'is_manager', 'is_warehouse', 'is_staff', 'is_superuser')
    list_filter = ('is_manager', 'is_warehouse', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone', 'birth_date')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_manager', 'is_warehouse', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )