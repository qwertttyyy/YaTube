from django.contrib import admin

from .models import Post, Group, Follow, Comment


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Отображает поля моделей в интерфейсе адиминстирования."""

    list_display = (
        'pk',
        'text',
        'created',
        'author',
        'group',
    )
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('created',)
    empty_value_display = '-пусто-'


admin.site.register(Group)
admin.site.register(Follow)
admin.site.register(Comment)
