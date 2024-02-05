from django.contrib.auth import get_user_model
from django.db import models

from core.models import CreatedModel
from .constants import MAX_GROUP_TITLE_LENGTH, POST_SYMBOLS_LIMIT

User = get_user_model()


class Group(models.Model):
    """Описывает модель Group для хранения групп."""

    title = models.CharField(
        max_length=MAX_GROUP_TITLE_LENGTH,
        verbose_name='Название сообщества'
    )
    slug = models.SlugField(unique=True, verbose_name='Сегмент пути')
    description = models.TextField(verbose_name='Описание сообщества')

    def __str__(self):
        return self.title


class Post(CreatedModel):
    """Описывает модель Post для хранения постов."""

    text = models.TextField(
        verbose_name='Текст поста',
        help_text='Введите текст поста',
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор'
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Сообщество',
        help_text='Группа, к которой будет относиться пост',
    )

    image = models.ImageField(
        upload_to='posts/',
        blank=True,
        verbose_name='Картинка'
    )

    class Meta:
        """Сортирует список постов по убыванию даты."""

        ordering = ['-created']

    def __str__(self):
        return self.text[:POST_SYMBOLS_LIMIT]


class Comment(CreatedModel):
    """Описывает модель Comment для хранения комментариев."""

    text = models.TextField(verbose_name='Текст комментария')

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор'
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
    )


class Follow(models.Model):
    """Описывает модель Follow для хранения подписок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
    )

    class Meta:
        unique_together = ('user', 'author')
