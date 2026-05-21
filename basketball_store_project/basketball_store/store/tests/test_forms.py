import pytest
from store.forms import CustomUserCreationForm, ReviewForm

@pytest.mark.django_db
def test_valid_registration_form():
    form = CustomUserCreationForm(data={
        'username': 'newuser',
        'email': 'new@example.com',
        'phone': '+375 (29) 111-22-33',
        'birth_date': '2000-01-01',
        'password1': 'strongpass123',
        'password2': 'strongpass123',
    })
    assert form.is_valid()

@pytest.mark.django_db
def test_invalid_phone_format():
    form = CustomUserCreationForm(data={
        'username': 'newuser2',   # уникальное имя, чтобы не конфликтовать
        'phone': '12345',
        'birth_date': '2000-01-01',
        'password1': 'pass',
        'password2': 'pass',
    })
    assert not form.is_valid()
    assert 'phone' in form.errors

@pytest.mark.django_db
def test_review_form_valid(user):
    form = ReviewForm(data={'rating': 5, 'text': 'Great sneakers!'})
    assert form.is_valid()