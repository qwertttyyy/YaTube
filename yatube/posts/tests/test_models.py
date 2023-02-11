from django.test import TestCase

from ..models import Group, Post, User
from ..constants import POST_SYMBOLS_LIMIT


class PostModelTest(TestCase):
    """Тестирование модели Post."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=('Тестовый пост. тестирование модели Post'
                  'Текст тестового поста для модели Post.')
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""

        test_data = {
            self.group.title: str(self.group),
            self.post.text[:POST_SYMBOLS_LIMIT]: str(self.post)
        }

        for model_value, str_value in test_data.items():
            with self.subTest(model_value=model_value):
                self.assertEqual(model_value, str_value)

    def test_verbose_name_post_model(self):
        """Verbose_name в полях совпадает с ожидаемым."""

        fields = {
            'text': 'Текст поста',
            'created': 'Дата публикации',
            'author': 'Автор',
            'group': 'Сообщество',
        }

        for field, expected_field in fields.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).verbose_name,
                    expected_field
                )

    def test_help_text_post_model(self):
        """Help_text в полях совпадает с ожидаемым."""

        fields = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост',
        }

        for field, expected_field in fields.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).help_text, expected_field)
