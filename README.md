# YaTube

## Описание проекта

YaTube – это социальная сеть, созданная для публикации личных дневников. Платформа предоставляет пользователям уникальную возможность создавать собственные страницы для публикации записей, делиться мыслями и моментами жизни. На YaTube каждый может стать автором своего уникального контента, делиться постами с изображениями, а также взаимодействовать с сообществом через подписки и комментарии.

### Основные функции:
- **Создание и редактирование постов** – Пользователи могут публиковать текстовые записи, прикреплять изображения и редактировать свои посты.
- **Подписки на авторов** – Возможность подписываться на интересующих авторов и следить за их обновлениями.
- **Комментирование постов** – Пользователи могут комментировать посты других авторов, обмениваясь мнениями и впечатлениями.
- **Создание уникальных страниц** – Каждый автор может выбрать себе имя и уникальный адрес для своей страницы.
- **Модерация и блокировка** – Функционал модерации записей и блокировки пользователей за спам.
- **Сообщества** – Возможность отправлять посты в сообщества и просматривать записи различных авторов.
- **Кеширование** – Реализовано кеширование для ускорения загрузки страниц.
- **Тестирование** – Написаны тесты с использованием `django.test` для проверки работоспособности ключевых функций.

### Технологический стек:

- Python
- Django
- SQLite

## Установка и запуск

### Шаг 1: Клонирование репозитория

```bash
git clone https://github.com/qwertttyyy/YaTube
cd yatube
```
Шаг 2: Установка зависимостей
```
pip install -r requirements.txt
```
Шаг 3: Применение миграций
```
python manage.py migrate
```
Шаг 4: Запуск сервера
```
python manage.py runserver
```
### Тестирование
Для запуска тестов выполните команду:
```
python manage.py test
```
