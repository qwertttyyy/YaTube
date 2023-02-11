from django.contrib.auth.forms import UserCreationForm

from posts.models import User


class CreationForm(UserCreationForm):
    """Создаёт форму для регистрации пользователей.
    Связывает с моделью Users."""

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')
