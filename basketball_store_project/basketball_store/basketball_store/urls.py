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
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)