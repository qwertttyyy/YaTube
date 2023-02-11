from django.core.paginator import Paginator


def page_pagination(request, page_objects, count):
    """Функция пагинатор, разбивает объекты по страницам."""

    paginator = Paginator(page_objects, count)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return page_obj
