import pytest
from django.contrib.auth import get_user_model
from store.models import Brand, Category, Sneaker, Size, SneakerSize, Order
from store.models import Vacancy, Review

User = get_user_model()

from datetime import date

@pytest.fixture
def user():
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        phone='+375 (29) 111-11-11',
        birth_date=date(2000, 1, 1),   # ← исправлено
        password='testpass123'
    )

@pytest.fixture
def brand():
    return Brand.objects.create(name='Nike', country='USA')

@pytest.fixture
def category():
    return Category.objects.create(name='Для игры', slug='playing')

@pytest.fixture
def sneaker(brand, category):
    return Sneaker.objects.create(
        brand=brand,
        model_name='Air Max',
        category=category,
        season='summer',
        price=15999,
        description='Test description'
    )

@pytest.fixture
def size():
    return Size.objects.create(size=42)

@pytest.fixture
def sneaker_size(sneaker, size):
    return SneakerSize.objects.create(sneaker=sneaker, size=size, stock=5)

@pytest.fixture
def order(user):
    return Order.objects.create(user=user, total_amount=0, status='pending')

@pytest.fixture
def manager_user():
    return User.objects.create_user(
        username='manager',
        email='manager@example.com',
        phone='+375 (29) 222-33-44',
        birth_date=date(1985, 5, 15),
        password='managerpass',
        is_manager=True
    )

@pytest.fixture
def warehouse_user():
    return User.objects.create_user(
        username='warehouse',
        email='warehouse@example.com',
        phone='+375 (29) 333-44-55',
        birth_date=date(1990, 7, 20),
        password='warehousepass',
        is_warehouse=True
    )

@pytest.fixture
def editor_user():
    return User.objects.create_user(
        username='editor',
        email='editor@example.com',
        phone='+375 (29) 444-55-66',
        birth_date=date(1988, 3, 10),
        password='editorpass',
        is_editor=True
    )

@pytest.fixture
def superuser(db):
    return User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        phone='+375 (29) 555-66-77',
        birth_date=date(1980, 1, 1),
        password='adminpass'
    )

@pytest.fixture
def vacancy():
    return Vacancy.objects.create(title='Test Vacancy', description='Test description')

@pytest.fixture
def review(user):
    return Review.objects.create(user=user, rating=5, text='Great!')