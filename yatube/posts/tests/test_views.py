from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from ..forms import PostForm
from ..models import Post, User, Group, Comment, Follow
from ..constants import NUMBER_OF_POSTS_ON_PAGE
from .constants import TEST_POSTS_COUNT


class PostPagesTest(TestCase):
    """Тестирование представлений приложения posts."""

    @classmethod
    def setUpClass(cls):
        """Создание тестового пользователя, поста и группы."""
        super().setUpClass()
        cls.user = User.objects.create(username='testuser')
        cls.user2 = User.objects.create(username='testuser2')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif')

        cls.post = Post.objects.create(
            text='Тестовый пост номер 1',
            author=cls.user,
            group=cls.group,
            image=uploaded
        )

    def setUp(self):
        """Авторизация тестового пользователя и
        создание поста через форму.
        """

        cache.clear()
        self.authorized_client = Client()
        self.authorized_client_2 = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_2.force_login(self.user2)

    def post_testing(self, post):
        """Вспомогательный метод для тестирования атрибутов поста."""

        self.assertEqual(post.id, self.post.id)
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.group, self.post.group)
        self.assertEqual(post.image, self.post.image)

    def test_pages_uses_correct_template(self):
        """Проверка, что во view-функциях
        используются правильные html-шаблоны.
        """

        template_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:profile', kwargs={'username': f'{self.user.username}'}
            ): 'posts/profile.html',

            reverse(
                'posts:group_list', kwargs={'slug': f'{self.group.slug}'}
            ): 'posts/group_list.html',

            reverse(
                'posts:post_detail', kwargs={'post_id': f'{self.post.id}'}
            ): 'posts/post_detail.html',

            reverse('posts:post_create'): 'posts/create_or_update_post.html',
            reverse('posts:post_edit', kwargs={'post_id': f'{self.post.id}'}):
                'posts/create_or_update_post.html'
        }

        for reverse_name, template in template_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Проверка контекста для страницы index."""

        response = self.authorized_client.get(reverse('posts:index'))
        posts = response.context['page_obj'].object_list
        self.post_testing(posts[0])

    def test_group_list_page_show_correct_context(self):
        """Проверка контекста для страницы group_list."""

        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': f'{self.group.slug}'})
        )
        posts = response.context['page_obj'].object_list
        self.assertEqual(
            len(posts),
            Post.objects.filter(group=self.group).count()
        )
        self.post_testing(posts[0])

        contex_group = response.context['group']
        self.assertEqual(contex_group.id, self.group.id)
        self.assertEqual(contex_group.title, self.group.title)
        self.assertEqual(contex_group.slug, self.group.slug)
        self.assertEqual(contex_group.description, self.group.description)

    def test_profile_page_show_correct_context(self):
        """Проверка контекста для страницы profile."""

        response = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': f'{self.user.username}'}
            )
        )
        posts = response.context['page_obj'].object_list
        self.assertEqual(len(posts), self.user.posts.all().count())
        self.post_testing(posts[0])

        author = response.context['author']
        self.assertEqual(author.username, self.user.username)

        Follow.objects.create(user=self.user, author=self.user2)
        context_following = response.context['following']
        following = Follow.objects.filter(
            user=self.user,
            author=author).exists()
        self.assertEqual(context_following, following)

    def test_post_detail_page_correct_context(self):
        """Проверка контекста для страницы post_detail."""

        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': f'{self.post.id}'})
        )
        context_post = response.context['post']
        self.post_testing(context_post)

        comment = Comment.objects.create(
            text='test post with comment',
            author=self.user,
            post=self.post
        )
        user_comment = response.context['comments'].get(id=comment.id)
        self.assertEqual(comment.text, user_comment.text)
        self.assertEqual(comment.author, user_comment.author)
        self.assertEqual(comment.post, user_comment.post)

    def test_create_post_page_correct_context(self):
        """Проверка формы на странице post_create."""

        response = self.authorized_client.get(reverse('posts:post_create'))
        self.assertIsInstance(response.context['form'], PostForm)

    def test_post_edit_page_correct_context(self):
        """Проверка формы на странице post_edit."""

        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': f'{self.post.id}'})
        )
        self.assertIsInstance(response.context['form'], PostForm)
        self.assertEqual(response.context['post_id'], self.post.id)

    def test_correct_pages_post_display(self):
        """Проверка, что пост отображается на ожидаемых страницах."""

        pages_list = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': f'{self.group.slug}'}),
            reverse(
                'posts:profile',
                kwargs={'username': f'{self.user.username}'}
            )
        ]

        new_post = Post.objects.create(
            text='Тестовый пост',
            author=self.user,
            group=self.group
        )

        for page in pages_list:
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                self.assertEqual(
                    new_post,
                    response.context['page_obj'].object_list[0]
                )

    def test_created_post_not_in_wrong_groups(self):
        """Проверка, что пост не попадает в неверную группу."""

        self.authorized_client.post(
            reverse('posts:post_create'),
            data={
                'text': 'Test post not wrong group',
                'group': self.group.id
            },
            follow=True
        )

        new_post = Post.objects.create(
            text='Тестовый пост',
            author=self.user,
            group=self.group
        )

        groups_without_post = Group.objects.exclude(id=self.group.id)
        self.assertNotIn(
            new_post,
            Post.objects.filter(group__in=groups_without_post)
        )

    def test_index_cached(self):
        """Проверка кеширования страницы index."""

        test_post = Post.objects.create(
            text='Тестовый пост для тестирования кэша',
            author=self.user,
        )

        response = self.authorized_client.get(reverse('posts:index'))
        Post.objects.filter(id=test_post.id).delete()
        response_after_delete = self.authorized_client.get(
            reverse('posts:index')
        )
        self.assertEqual(response.content, response_after_delete.content)

        cache.clear()

        response_after_cache_clear = self.authorized_client.get(
            reverse('posts:index')
        )

        self.assertNotEqual(
            response.content,
            response_after_cache_clear.content
        )

    def test_user_can_follow(self):
        """Проверка, что пользователь может
        подписываться на других пользователей."""

        follows_before = list(Follow.objects.values_list('id', flat=True))

        self.authorized_client.get(reverse(
            'posts:profile_follow',
            args=[self.user2.username]
        ))

        follows = Follow.objects.exclude(id__in=follows_before)
        self.assertEqual(follows[0].user, self.user)
        self.assertEqual(follows[0].author, self.user2)
        self.assertEqual(len(follows), len(follows_before) + 1)

    def test_user_can_unfollow(self):
        """Проверка, что пользователь может
        отписываться от других пользователей."""

        follow = Follow.objects.create(user=self.user, author=self.user2)
        follows_before = list(Follow.objects.values_list('id', flat=True))

        self.authorized_client.get(reverse(
            'posts:profile_unfollow',
            args=[self.user2.username]
        ))

        follows = Follow.objects.exclude(id__in=follows_before)
        self.assertNotIn(follow, follows)
        self.assertEqual(len(follows), len(follows_before) - 1)

    def test_new_post_in_follower_feed(self):
        """Новая запись появляется в ленте подписчиков."""

        new_post = Post.objects.create(
            text='Follow test post',
            author=self.user2
        )
        Follow.objects.create(user=self.user, author=self.user2)
        follower_feed = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        feed_post = follower_feed.context['page_obj'].object_list[0]
        self.assertEqual(feed_post.id, new_post.id)
        self.assertEqual(feed_post.text, new_post.text)
        self.assertEqual(feed_post.author, new_post.author)

    def test_new_post_not_in_not_follower_feed(self):
        """Новая запись не появляется в ленте тех, кто не подписан."""

        new_post = Post.objects.create(
            text='Follow test post',
            author=self.user2
        )

        not_follower_feed = self.authorized_client.get(
            reverse('posts:follow_index')
        )

        self.assertNotIn(
            new_post,
            not_follower_feed.context['page_obj'].object_list
        )


class PaginatorViewTest(TestCase):
    """Тестирование паджинатора."""

    @classmethod
    def setUpClass(cls):
        cache.clear()
        super().setUpClass()
        cls.user = User.objects.create_user(username='testuser2')
        cls.group = Group.objects.create(
            title='title2',
            description='description',
            slug='test-slug2'
        )

        posts = [
            Post(
                author=cls.user,
                text='Test post. Paginator test.',
                group=cls.group
            )
            for _ in range(TEST_POSTS_COUNT)
        ]
        Post.objects.bulk_create(posts)

    def test_first_page_correct_paginate(self):
        """Проверка, что паджинатор работает корректно."""
        pages_list = [
            reverse('posts:index'),
            reverse('posts:group_list',
                    kwargs={'slug': f'{self.group.slug}'}),
            reverse(
                'posts:profile',
                kwargs={'username': f'{self.user.username}'}
            )
        ]

        for page in pages_list:
            with self.subTest(page=page):
                response = self.client.get(page)
                page = response.context['page_obj']
                self.assertEqual(len(page), NUMBER_OF_POSTS_ON_PAGE)

    def test_second_page_pagination(self):
        pages_list = [
            reverse('posts:index'),
            reverse('posts:group_list',
                    kwargs={'slug': f'{self.group.slug}'}),
            reverse(
                'posts:profile',
                kwargs={'username': f'{self.user.username}'}
            )
        ]

        for page in pages_list:
            with self.subTest(page=page):
                response = self.client.get(page + '?page=2')
                page = response.context['page_obj']
                self.assertEqual(
                    len(page),
                    TEST_POSTS_COUNT - NUMBER_OF_POSTS_ON_PAGE
                )
