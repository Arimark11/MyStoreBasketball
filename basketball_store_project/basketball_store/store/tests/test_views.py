import pytest
from django.urls import reverse
from store.models import Review, Sneaker
from store.models import Vacancy, JobApplication

@pytest.mark.django_db
def test_home_page_status(client):
    url = reverse('home')
    response = client.get(url)
    assert response.status_code == 200

@pytest.mark.django_db
def test_catalog_view(client, sneaker):
    url = reverse('catalog')
    response = client.get(url)
    assert response.status_code == 200
    assert 'sneakers' in response.context
    assert sneaker in response.context['sneakers']

@pytest.mark.django_db
def test_catalog_search(client, sneaker):
    url = reverse('catalog')
    response = client.get(url, {'search': 'Air Max'})
    assert response.status_code == 200
    assert sneaker in response.context['sneakers']

@pytest.mark.django_db
def test_cart_view_requires_login(client):
    url = reverse('cart_view')
    response = client.get(url)
    # Если вы добавили @login_required к cart_view, то редирект 302
    # Если нет – ожидайте 200, но лучше добавить декоратор
    assert response.status_code == 302
    assert response.url.startswith('/login/')


@pytest.mark.django_db
def test_cart_add_authenticated(client, user, sneaker_size):
    client.force_login(user)
    url = reverse('cart_add')
    response = client.post(url, {'sneaker_size_id': sneaker_size.id, 'quantity': 2})
    assert response.status_code == 302
    assert response.url == reverse('catalog')
    # Проверяем сессию
    cart = client.session.get('cart', {})
    assert str(sneaker_size.id) in cart
    assert cart[str(sneaker_size.id)] == 2

@pytest.mark.django_db
def test_checkout_decreases_stock(client, user, sneaker_size):
    client.force_login(user)
    # Добавляем в корзину
    session = client.session
    session['cart'] = {str(sneaker_size.id): 2}
    session.save()
    url = reverse('checkout')
    response = client.get(url)
    assert response.status_code == 200
    sneaker_size.refresh_from_db()
    assert sneaker_size.stock == 3  # было 5, заказали 2

@pytest.mark.django_db
def test_profile_requires_login(client):
    url = reverse('profile')
    response = client.get(url)
    assert response.status_code == 302
    assert response.url.startswith('/login/')

@pytest.mark.django_db
def test_profile_authenticated(client, user):
    client.force_login(user)
    url = reverse('profile')
    response = client.get(url)
    assert response.status_code == 200
    assert 'user' in response.context

@pytest.mark.django_db
def test_profile_edit_requires_login(client):
    url = reverse('profile_edit')
    response = client.get(url)
    assert response.status_code == 302

@pytest.mark.django_db
def test_profile_edit_authenticated(client, user):
    client.force_login(user)
    url = reverse('profile_edit')
    response = client.get(url)
    assert response.status_code == 200

# ========== ТЕСТЫ ДЛЯ УПРАВЛЕНИЯ ЗАКАЗАМИ (только менеджер/админ) ==========

@pytest.mark.django_db
def test_manage_orders_requires_manager(client, user):
    client.force_login(user)
    url = reverse('manage_orders')
    response = client.get(url)
    assert response.status_code == 302  # редирект для обычного пользователя

@pytest.mark.django_db
def test_manage_orders_manager_access(client, manager_user):
    client.force_login(manager_user)
    url = reverse('manage_orders')
    response = client.get(url)
    assert response.status_code == 200

@pytest.mark.django_db
def test_update_order_status_requires_manager(client, manager_user, order):
    client.force_login(manager_user)
    url = reverse('update_order_status', args=[order.id])
    response = client.post(url, {'status': 'paid'})
    assert response.status_code == 302  # редирект после обновления
    order.refresh_from_db()
    assert order.status == 'paid'

# ========== ТЕСТЫ ДЛЯ УПРАВЛЕНИЯ СКЛАДОМ (только сотрудник склада/админ) ==========

@pytest.mark.django_db
def test_manage_stock_requires_warehouse(client, user):
    client.force_login(user)
    url = reverse('manage_stock')
    response = client.get(url)
    assert response.status_code == 302

@pytest.mark.django_db
def test_manage_stock_warehouse_access(client, warehouse_user):
    client.force_login(warehouse_user)
    url = reverse('manage_stock')
    response = client.get(url)
    assert response.status_code == 200

@pytest.mark.django_db
def test_update_stock_warehouse(client, warehouse_user, sneaker_size):
    client.force_login(warehouse_user)
    url = reverse('update_stock')
    data = {f'stock_{sneaker_size.id}': 10}
    response = client.post(url, data)
    assert response.status_code == 302
    sneaker_size.refresh_from_db()
    assert sneaker_size.stock == 10

# ========== ТЕСТЫ ДЛЯ УПРАВЛЕНИЯ ЗАЯВКАМИ (только суперпользователь) ==========

@pytest.mark.django_db
def test_manage_applications_requires_superuser(client, user):
    client.force_login(user)
    url = reverse('manage_applications')
    response = client.get(url)
    assert response.status_code == 302

@pytest.mark.django_db
def test_manage_applications_superuser_access(client, superuser):
    client.force_login(superuser)
    url = reverse('manage_applications')
    response = client.get(url)
    assert response.status_code == 200

# ========== ТЕСТЫ ДЛЯ ПОДАЧИ ЗАЯВКИ НА ВАКАНСИЮ ==========

@pytest.mark.django_db
def test_apply_for_vacancy_requires_login(client, vacancy):
    url = reverse('apply_vacancy', args=[vacancy.id])
    response = client.get(url)
    assert response.status_code == 302

@pytest.mark.django_db
def test_apply_for_vacancy_authenticated(client, user, vacancy):
    client.force_login(user)
    url = reverse('apply_vacancy', args=[vacancy.id])
    response = client.get(url)
    assert response.status_code == 200
    response = client.post(url, {'comment': 'I want this job'})
    assert response.status_code == 302
    assert JobApplication.objects.filter(user=user, vacancy=vacancy).exists()

# ========== ТЕСТ ДЛЯ УДАЛЕНИЯ ОТЗЫВА (только редактор/админ) ==========

@pytest.mark.django_db
def test_delete_review_requires_editor(client, user, review):
    client.force_login(user)
    url = reverse('delete_review', args=[review.id])
    response = client.post(url)
    assert response.status_code == 302  # редирект для не-редактора

@pytest.mark.django_db
def test_delete_review_editor_access(client, editor_user, review):
    client.force_login(editor_user)
    url = reverse('delete_review', args=[review.id])
    response = client.post(url)
    assert response.status_code == 302
    assert not Review.objects.filter(id=review.id).exists()

# ========== ТЕСТ ДЛЯ СТРАНИЦЫ АНАЛИТИКИ (только суперпользователь) ==========

@pytest.mark.django_db
def test_analytics_requires_superuser(client, user):
    client.force_login(user)
    url = reverse('analytics')
    response = client.get(url)
    assert response.status_code == 302

@pytest.mark.django_db
def test_analytics_superuser_access(client, superuser):
    client.force_login(superuser)
    url = reverse('analytics')
    response = client.get(url)
    assert response.status_code == 200

# ========== ТЕСТЫ ДЛЯ ПУБЛИЧНЫХ СТРАНИЦ ==========

@pytest.mark.django_db
def test_about_page(client):
    url = reverse('about')
    response = client.get(url)
    assert response.status_code == 200

@pytest.mark.django_db
def test_contacts_page(client):
    url = reverse('contacts')
    response = client.get(url)
    assert response.status_code == 200

@pytest.mark.django_db
def test_vacancies_page(client):
    url = reverse('vacancies')
    response = client.get(url)
    assert response.status_code == 200

@pytest.mark.django_db
def test_promocodes_page(client):
    url = reverse('promocodes')
    response = client.get(url)
    assert response.status_code == 200

@pytest.mark.django_db
def test_privacy_page(client):
    url = reverse('privacy')
    response = client.get(url)
    assert response.status_code == 200

@pytest.mark.django_db
def test_glossary_page(client):
    url = reverse('glossary')
    response = client.get(url)
    assert response.status_code == 200

# ========== ТЕСТЫ ДЛЯ НОВОСТЕЙ (детали) ==========

@pytest.mark.django_db
def test_news_detail(client, sneaker):
    # создадим новость, но проще использовать существующую фикстуру News
    from store.models import News
    news = News.objects.create(title='Test', summary='Test', full_text='Test')
    url = reverse('news_detail', args=[news.id])
    response = client.get(url)
    assert response.status_code == 200

# ========== ТЕСТ ДЛЯ sneaker_detail (re_path) ==========

@pytest.mark.django_db
def test_sneaker_detail(client, sneaker):
    url = reverse('sneaker_detail', args=[sneaker.id])
    response = client.get(url)
    assert response.status_code == 200
    assert response.context['sneaker'] == sneaker

# ========== ТЕСТ ДЛЯ КОРЗИНЫ: УДАЛЕНИЕ ТОВАРА ==========

@pytest.mark.django_db
def test_cart_remove(client, user, sneaker_size):
    client.force_login(user)
    session = client.session
    session['cart'] = {str(sneaker_size.id): 2}
    session.save()
    url = reverse('cart_remove', args=[sneaker_size.id])
    response = client.get(url)
    assert response.status_code == 302
    cart = client.session.get('cart', {})
    assert str(sneaker_size.id) not in cart

# ========== ТЕСТ ДЛЯ ПРОВЕРКИ ОСТАТКОВ ПРИ ОФОРМЛЕНИИ ==========

@pytest.mark.django_db
def test_checkout_insufficient_stock(client, user, sneaker_size):
    client.force_login(user)
    # Устанавливаем маленький остаток
    sneaker_size.stock = 1
    sneaker_size.save()
    session = client.session
    session['cart'] = {str(sneaker_size.id): 5}  # хотим больше, чем есть
    session.save()
    url = reverse('checkout')
    response = client.get(url)
    assert response.status_code == 302  # редирект на корзину с ошибкой