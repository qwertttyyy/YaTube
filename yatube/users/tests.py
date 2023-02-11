from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from posts.models import User


class UsersPagesTest(TestCase):
    """Тестирование страниц приложения users."""

    def setUp(self):
        """Создание гостевого клиента."""

        self.guest_client = Client()

    def test_pages_uses_correct_template(self):
        """Проверка, что по ссылкам отображаются ожидаемые шаблоны."""

        template_pages_names = {
            'users/login.html': reverse('users:login'),
            'users/signup.html': reverse('users:signup'),
            'users/password_reset_form.html': reverse(
                'users:password_reset_form'
            ),
        }

        for template, reverse_name in template_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_signup_form(self):
        """Проверка, что на странице регистрации
        форма отображается корректно.
        """

        response = self.guest_client.get(reverse('users:signup'))

        form_fields = {
            'first_name': forms.fields.CharField,
            'last_name': forms.fields.CharField,
            'username': forms.fields.CharField,
            'email': forms.fields.CharField
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)


class UserCreateFormTest(TestCase):
    """Тестирование создания нового пользователя."""

    def setUp(self):
        """Создание гостевого клиента."""

        self.guest_client = Client()

    def test_user_create(self):
        """Проверка, что новый пользователь создаётся."""

        form_data = {
            'username': 'testuser',
            'password1': 'testpassword',
            'password2': 'testpassword'
        }

        response = self.guest_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )

        self.assertRedirects(response, reverse('posts:index'))
        self.assertTrue(User.objects.filter(username=form_data['username']))
