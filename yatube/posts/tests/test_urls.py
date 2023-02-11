from http import HTTPStatus

from django.urls import reverse
from django.test import TestCase, Client
from django.core.cache import cache

from ..models import User, Post, Group


class PostURLTests(TestCase):
    """Тестирование адресов приложения posts"""

    @classmethod
    def setUpClass(cls):
        """Создание тестового пользователя, поста и группы."""

        super().setUpClass()
        cls.user = User.objects.create(username='TestUser')
        cls.user_2 = User.objects.create(username='TestUser2')
        cls.post = Post.objects.create(
            author=cls.user,
            text=('Тестовый пост. тестирование модели Post'
                  'Текст тестового поста для модели Post.')
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )

    def setUp(self):
        """Создание гостевого клиента и авторизация тестового пользователя."""

        cache.clear()
        self.authorized_client = Client()
        self.authorized_client_2 = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_2.force_login(self.user_2)

    def test_public_urls_existence(self):
        """Проверка, что страницы дают ожидаемый статус."""

        urls_statuses = {
            '/': HTTPStatus.OK,
            f'/group/{self.group.slug}/': HTTPStatus.OK,
            f'/profile/{self.user.username}/': HTTPStatus.OK,
            f'/posts/{self.post.id}/': HTTPStatus.OK,
            '/nonexistent_page/': HTTPStatus.NOT_FOUND,
            '/create/': HTTPStatus.FOUND,
            f'/posts/{self.post.id}/edit/': HTTPStatus.FOUND,
        }

        for url, status in urls_statuses.items():
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, status)

    def test_post_creat_page_availability(self):
        """Проверка, что страница создания работает
         для авторизованного пользователя."""

        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_page_availability(self):
        """Проверка, что страница редактирования поста работает и
        доступна только автору поста."""

        response = self.authorized_client.get(f'/posts/{self.post.id}/edit/')
        error = 'Авторизованный пользователь не является автором поста'
        self.assertEqual(response.status_code, HTTPStatus.OK, error)

    def test_urls_uses_correct_template(self):
        """Проверка, что по ссылкам отображаются ожидаемые шаблоны."""

        templates_url_name = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_or_update_post.html',
            '/create/': 'posts/create_or_update_post.html',
            '/not-found/': 'core/404.html',
        }

        for address, template in templates_url_name.items():
            with self.subTest(address=address):
                error = (
                    f'Страница {address} должна использовать шаблон {template}'
                )
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template, error)

    def test_guest_private_pages_redirect(self):
        """Проверка редиректа гостя на страницу авторизации
        при попытке перейти на приватные страницы."""

        urls_redirect = [
            reverse('posts:post_create'),
            reverse('posts:post_edit', args=[self.post.id])
        ]

        for url in urls_redirect:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertRedirects(
                    response,
                    f'{reverse("users:login")}?next={url}'
                )

    def test_not_author_access(self):
        """Проверка редиректа не автора поста
        при попытке редактирования."""

        response = self.authorized_client_2.get(reverse(
            'posts:post_edit', args=[self.post.id]
        ))
        self.assertRedirects(response, reverse(
            'posts:post_detail', args=[self.post.id]
        ))

    def test_only_authorized_users_can_comment(self):
        """Проверка, что авторизованные пользователи
         могут комментировать посты."""

        response = self.authorized_client.get(reverse(
            'posts:add_comment',
            args=[self.post.id])
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', args=[self.post.id])
        )
