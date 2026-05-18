from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Review
from datetime import date

# Форма регистрации с валидацией телефона и возраста
class CustomUserCreationForm(UserCreationForm):
    phone = forms.CharField(max_length=20, label='Телефон')
    birth_date = forms.DateField(label='Дата рождения', widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'phone', 'birth_date', 'password1', 'password2')

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if not phone.startswith('+375 (29)'):
            raise forms.ValidationError('Формат телефона: +375 (29) XXX-XX-XX')
        return phone

    def clean_birth_date(self):
        bd = self.cleaned_data['birth_date']
        age = (date.today() - bd).days // 365
        if age < 18:
            raise forms.ValidationError('Возраст должен быть 18+')
        return bd

# Форма редактирования профиля
class CustomUserChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'birth_date']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'phone': forms.TextInput(attrs={'placeholder': '+375 (29) 111-11-11'}),
        }

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if not phone.startswith('+375 (29)'):
            raise forms.ValidationError('Формат телефона: +375 (29) XXX-XX-XX')
        return phone

    def clean_birth_date(self):
        bd = self.cleaned_data['birth_date']
        age = (date.today() - bd).days // 365
        if age < 18:
            raise forms.ValidationError('Возраст должен быть 18+')
        return bd

# Форма отзыва (была ранее)
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Ваш отзыв...'}),
            'rating': forms.Select(choices=[(i, f"{i} ★") for i in range(1, 6)]),
        }