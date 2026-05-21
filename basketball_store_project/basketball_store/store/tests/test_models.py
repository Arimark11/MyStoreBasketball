import pytest
from datetime import date
from django.core.exceptions import ValidationError
from store.models import User
from store.models import Sneaker

@pytest.mark.django_db
def test_user_age():
    user = User(username='test', birth_date=date(2000, 1, 1))
    assert user.age == (date.today().year - 2000) - ((date.today().month, date.today().day) < (1, 1))

@pytest.mark.django_db
def test_user_save_age_validation():
    user = User(username='test', birth_date=date.today())
    with pytest.raises(ValueError, match="Возраст должен быть 18+"):
        user.save()

@pytest.mark.django_db
def test_sneaker_str(brand, category):
    sneaker = Sneaker(brand=brand, model_name='Air Max', category=category)
    assert str(sneaker) == 'Nike Air Max'

@pytest.mark.django_db
def test_sneaker_size_stock(sneaker_size):
    assert sneaker_size.stock == 5