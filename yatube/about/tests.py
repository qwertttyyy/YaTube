from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse


class AboutURLTest(TestCase):
    """Тестирование страниц 'Об авторе' и 'Технологии'."""

    def setUp(self):
        """Создание гостевого клиента."""

        self.guest_client = Client()

    def test_about_urls_exists_at_desired_location(self):
        """Проверка доступности адресов /about/author/ и /about/tech/."""

        page_addresses = ["/about/author/", "/about/tech/"]
        for address in page_addresses:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_urls_uses_correct_template(self):
        """Проверка шаблона для адресов /about/author/ и /about/tech/."""
        templates_urls_names = {
            "/about/author/": "about/about.html",
            "/about/tech/": "about/tech.html",
        }

        for address, template in templates_urls_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)


class AboutPagesTest(TestCase):
    """Тестирование представлений приложения about"""

    def setUp(self):
        """Создание гостевого клиента."""
        self.guest_client = Client()

    def test_pages_uses_correct_template(self):
        """Проверка, что страницы отображаются по ссылкам."""

        template_pages_names = {
            "about/about.html": reverse("about:author"),
            "about/tech.html": reverse("about:tech"),
        }

        for template, reverse_name in template_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
