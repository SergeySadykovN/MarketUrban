# shop/forms.py

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', )


CHOICES_PAYMENT = (
    ('Card', 'Кредитная карта'),
    ('COD', 'Наличные при получении'),
)

class CheckoutForm(forms.Form):
    delivery_address = forms.CharField(label='Адрес доставки', max_length=100)
    phone_number = forms.CharField(label='Номер телефона', max_length=15)
    payment_option = forms.ChoiceField(label='Метод оплаты', choices=CHOICES_PAYMENT)