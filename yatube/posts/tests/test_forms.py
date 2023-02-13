import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client, override_settings
from django.urls import reverse

from ..models import Post, User, Group, Comment

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    """Тестирование форм для создания и редактирования постов."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='testuser')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        """Создаётся и логиниться тестовый пользователь."""

        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Проверка, что пост создаётся."""

        posts_ids = list(Post.objects.values_list('id', flat=True))

        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=self.small_gif,
            content_type='image/gif'
        )

        form_data = {
            'text': 'Test text 123456',
            'group': self.group.id,
            'image': uploaded,
        }

        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )

        posts = Post.objects.exclude(id__in=posts_ids)
        self.assertEqual(len(posts), 1)
        new_post = posts[0]
        self.assertEqual(new_post.text, form_data['text'])
        self.assertEqual(new_post.group.id, form_data['group'])
        self.assertEqual(new_post.author, self.user)
        self.assertEqual(new_post.image, 'posts/small.gif')

        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': f'{self.user.username}'}
        ))

    def test_edit_post(self):
        """Проверка, что пост редактируется."""

        post = Post.objects.create(
            text='post test text',
            author=self.user
        )

        form_data = {
            'text': 'edited text',
            'group': self.group.id,
        }

        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post.id}),
            data=form_data,
            follow=True
        )

        edited_post = Post.objects.get(id=post.id)
        self.assertEqual(edited_post.text, form_data['text'])
        self.assertEqual(edited_post.group.id, form_data['group'])
        self.assertEqual(edited_post.author, self.user)
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            args=[edited_post.id]
        ))

    def test_only_authorized_users_can_comment(self):
        """Проверка, что только авторизованные
        пользователи могут комментировать посты."""

        test_post = Post.objects.create(
            text='test post comment',
            author=self.user
        )

        comment_count = Comment.objects.count()

        form_data = {
            'text': 'test comment',
            'post': test_post.id,
        }

        self.client.post(
            reverse('posts:add_comment', args=[test_post.id]),
            data=form_data,
            follow=True
        )

        self.assertEqual(comment_count, Comment.objects.count())

        self.authorized_client.post(
            reverse('posts:add_comment', args=[test_post.id]),
            data=form_data,
            follow=True
        )

        self.assertEqual(comment_count + 1, Comment.objects.count())
        comment = Comment.objects.all()[0]
        self.assertEqual(comment.post, test_post)
