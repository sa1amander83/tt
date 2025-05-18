from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password


from accounts.models import User


from django import forms
from django.contrib.auth import authenticate

from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator


class SignInForm(forms.Form):
    login_email = forms.EmailField(
        label="Email",
        required=False,
        widget=forms.EmailInput(attrs={
            "class": "w-full px-3 py-2 border border-2 border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500",
            "id": "loginEmailField",
            "placeholder": "example@example.com"
        })
    )
    login_phone = forms.CharField(
        label="Телефон",
        required=False,
        validators=[
            RegexValidator(
                regex=r'^\d{10}$',
                message="Введите 10 цифр номера телефона без +7"
            )
        ],
        widget=forms.TextInput(attrs={
            "class": "w-full px-3 py-2 border border-2 border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500",
            "id": "loginPhoneField",
            "placeholder": "9XXXXXXXXX",
            "maxlength": "10"
        })
    )
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={
            "class": "w-full px-3 py-2 border border-2 border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
        })
    )
    login_method = forms.CharField(widget=forms.HiddenInput())

    def clean(self):
        cleaned_data = super().clean()
        method = cleaned_data.get('login_method')
        login_email = cleaned_data.get('login_email')
        login_phone = cleaned_data.get('login_phone')

        # Проверяем, что выбран метод входа
        if not method:
            raise ValidationError("Не выбран метод входа")

        if method == 'email':
            if not login_email:
                raise ValidationError("Введите email")
            cleaned_data['login'] = login_email
        elif method == 'phone':
            if not login_phone:
                raise ValidationError("Введите номер телефона")
            cleaned_data['login'] =  login_phone
        else:
            raise ValidationError("Неверный метод входа")

        return cleaned_data



class SignUpForm(forms.ModelForm):

    LEVEL_CHOICES = [
        ('beginner', 'Начинающий'),
        ('intermediate', 'Средний'),
        ('advanced', 'Продвинутый'),
        ('professional', 'Профессиональный'),
    ]
    user_name = forms.CharField(
        label="Имя и фамилия",
        widget=forms.TextInput(attrs={
            "class": "w-full px-3 py-2 border border-2 border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500"
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "class": "w-full px-3 py-2 border border-2 border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500"
        })
    )
    phone = forms.CharField(
        label="Номер телефона",
        validators=[
            RegexValidator(
                regex=r'^\d{10}$',
                message="Введите 10 цифр номера без +7"
            )
        ],
        widget=forms.TextInput(attrs={
            "class": "flex-1 px-3 py-2 border border-2 border-gray-300 rounded-r-md focus:outline-none focus:ring-green-500 focus:border-green-500",
            "placeholder": "9XXXXXXXXX",
            "maxlength": "10"
        })
    )

    user_age = forms.IntegerField(
        label="Возраст",
        required=False,  # если поле необязательное
        validators=[
            MinValueValidator(5, message="Возраст должен быть не меньше 5 лет"),
            MaxValueValidator(99, message="Возраст должен быть не больше 99 лет"),
        ],
        widget=forms.NumberInput(attrs={
            "class": "w-full px-3 py-2 border border-2 border-gray-300 rounded-md focus:outline-none focus:ring-green-500 focus:border-green-500",
            "placeholder": "18",
            "maxlength": "2"
        })
    )

    level = forms.ChoiceField(
        label="Уровень",
        choices=LEVEL_CHOICES,
        initial='beginner',
        widget=forms.Select(attrs={
            "class": "w-full px-3 py-2 border border-2 border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500"
        })
    )


    password1 = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={
            "class": "w-full px-3 py-2 border border-2 border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500"
        }),
        validators=[validate_password]
    )
    password2 = forms.CharField(
        label="Подтверждение пароля",
        widget=forms.PasswordInput(attrs={
            "class": "w-full px-3 py-2 border border-2 border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500"
        })
    )
    terms = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            "class": "h-4 w-4 text-green-600 focus:ring-green-500 border-2 border-gray-300 rounded mt-1"
        })
    )

    class Meta:
        model = User
        fields = ['user_name', 'email', 'phone', 'level', 'user_age']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("Пользователь с таким email уже зарегистрирован.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')

        if User.objects.filter(phone=phone).exists():
            raise ValidationError("Пользователь с таким номером телефона уже зарегистрирован.")
        return phone



    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError("Пароли не совпадают")
        return password2



    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.level = self.cleaned_data["level"]  # Сохраняем уровень

        if commit:
            user.save()
        return user


class ProfileUpdateForm(forms.ModelForm):


    phone = forms.CharField(
        label="Телефон",
        validators=[
            RegexValidator(
                regex=r'^\+7\d{10}$',
                message="Номер должен быть в формате: '+79991234567' (10 цифр после +7)"
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-2 border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500',
            'placeholder': '+79991234567',
            'data-field': 'phone'  # Добавляем data-атрибут для JS
        })
    )

    level = forms.ChoiceField(
        label="Уровень игры",
        choices=[
            ('beginner', 'Начинающий'),
            ('intermediate', 'Средний'),
            ('advanced', 'Продвинутый'),
            ('professional', 'Профессиональный'),
        ],
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-2 border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500',
            'data-field': 'level'
        })
    )

    class Meta:
        model = User
        fields = ['user_name', 'email', 'phone', 'level']
        widgets = {
            'user_name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-2 border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500',
                'placeholder': 'Иван Иванов',
                'data-field': 'user_name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-3 py-2 border border-2 border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500',
                'placeholder': 'example@example.com',
                'data-field': 'email'
            }),
        }
        labels = {
            'user_name': 'ФИО',
            'email': 'Email'
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone.startswith('+7') or len(phone) != 12:
            raise ValidationError("Номер должен быть в формате: '+79991234567' (10 цифр после +7)")
        return phone

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError("Этот email уже используется другим пользователем")
        return email

class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.update({
            'class': 'w-full px-3 py-2 border border-2 border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500'
        })
        self.fields['new_password1'].widget.attrs.update({
            'class': 'w-full px-3 py-2 border border-2 border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500'
        })
        self.fields['new_password2'].widget.attrs.update({
            'class': 'w-full px-3 py-2 border border-2 border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500'
        })

from django.core.validators import FileExtensionValidator

class ProfilePhotoForm(forms.ModelForm):
    photo = forms.ImageField(
        label="Фото профиля",
        required=False,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])],
        widget=forms.FileInput(attrs={
            'class': 'hidden',
            'id': 'photo-upload',
            'accept': 'image/*'
        })
    )

    class Meta:
        model = User
        fields = ['photo']