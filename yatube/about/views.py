from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    """Создаёт страницу с информацией об авторе."""

    template_name = 'about/about.html'


class AboutTechView(TemplateView):
    """Создаёт страницу со списком навыков и используемых технологий."""

    template_name = 'about/tech.html'
