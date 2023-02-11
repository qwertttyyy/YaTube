from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    """Описывает форму для создания/редактирования поста."""

    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        help_texts = {
            'text': 'Текст нового поста',
            'group': 'Группа, к которой будет относиться пост'
        }


class CommentForm(forms.ModelForm):
    """Описывает форму для создания/редактирования комментария."""

    class Meta:
        model = Comment
        fields = ('text',)
