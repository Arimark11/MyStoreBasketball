from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView, LogoutView
from store import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('news/', views.NewsListView.as_view(), name='news_list'),
    path('news/<int:pk>/', views.NewsDetailView.as_view(), name='news_detail'),
    path('glossary/', views.glossary, name='glossary'),
    path('contacts/', views.contacts, name='contacts'),
    path('vacancies/', views.vacancies, name='vacancies'),
    path('reviews/', views.reviews_view, name='reviews'),
    path('add-review/', views.add_review, name='add_review'),
    path('promocodes/', views.promocodes, name='promocodes'),
    path('privacy/', views.privacy, name='privacy'),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    #path('logout/', LogoutView.as_view(), name='logout'),
    path('logout/', views.custom_logout, name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.ProfileUpdateView.as_view(), name='profile_edit'),
    path('analytics/', views.analytics, name='analytics'),
    path('catalog/', views.catalog, name='catalog'),
    path('cart/', views.cart_view, name='cart_view'),
    path('cart/add/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:sneaker_size_id>/', views.cart_remove, name='cart_remove'),
    path('checkout/', views.checkout, name='checkout'),
    path('manage-orders/', views.manage_orders, name='manage_orders'),
    path('update-order-status/<int:order_id>/', views.update_order_status, name='update_order_status'),
    path('apply/<int:vacancy_id>/', views.apply_for_vacancy, name='apply_vacancy'),
    path('manage-applications/', views.manage_applications, name='manage_applications'),
    path('update-application/<int:application_id>/', views.update_application_status, name='update_application'),
    path('manage-stock/', views.manage_stock, name='manage_stock'),
    path('update-stock/', views.update_stock, name='update_stock'),
    path('news/create/', views.NewsCreateView.as_view(), name='news_create'),
    path('news/<int:pk>/edit/', views.NewsUpdateView.as_view(), name='news_update'),
    path('news/<int:pk>/delete/', views.NewsDeleteView.as_view(), name='news_delete'),
    path('review/delete/<int:review_id>/', views.delete_review, name='delete_review'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)