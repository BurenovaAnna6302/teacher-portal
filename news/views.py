from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.http import JsonResponse
import json
from datetime import datetime
from .models import News, TargetAudience, ContentType, InfoStatus


def get_status_color(status_name):
    """Функция для получения цвета статуса"""
    colors = {
        'Экстренные': 'rgba(255, 200, 200, 0.85)',
        'Важные': 'rgba(255, 230, 200, 0.85)',
        'Новости': 'rgba(201, 228, 202, 0.85)',
        'Аналитика': 'rgba(200, 220, 240, 0.85)',
        'Анонсы': 'rgba(240, 240, 180, 0.85)',
        'Документы': 'rgba(220, 240, 220, 0.85)',
        'Отчеты': 'rgba(240, 220, 220, 0.85)',
        'Рекомендации': 'rgba(230, 220, 240, 0.85)',
    }
    return colors.get(status_name, 'rgba(200, 200, 200, 0.85)')


def get_status_text_color(status_name):
    """Возвращает яркий цвет текста для статуса"""
    text_colors = {
        'Экстренные': '#cc0000',  # темно-красный
        'Важные': '#ff6600',  # оранжевый
        'Новости': '#1e8c1e',  # темно-зеленый
        'Аналитика': '#0066cc',  # синий
        'Анонсы': '#cc9900',  # золотой
        'Документы': '#009900',  # зеленый
        'Отчеты': '#cc3366',  # розовый
        'Рекомендации': '#6600cc',  # фиолетовый
    }
    return text_colors.get(status_name, '#000000')


def news_list(request):
    """
    Страница списка новостей - только первая загрузка.
    Все данные передаются в контекст для первоначального рендера.
    """

    # Получаем все справочники из БД
    target_audiences = TargetAudience.objects.all()
    content_types = ContentType.objects.all()
    info_statuses = InfoStatus.objects.all()

    # Добавляем цвет и цвет текста к каждому статусу
    for status in info_statuses:
        status.color = get_status_color(status.name)
        status.text_color = get_status_text_color(status.name)

    # Получаем только первую страницу новостей для первоначальной загрузки
    news_queryset = News.objects.filter(is_published=True).select_related(
        'target_audience', 'content_type', 'info_status'
    ).prefetch_related('photos').order_by('-publication_date')

    paginator = Paginator(news_queryset, 9)
    first_page = paginator.get_page(1)

    # Подготовка данных для первой страницы (для JavaScript)
    first_page_data = []
    for news in first_page:
        first_photo = news.photos.first()
        image_url = None
        if first_photo and first_photo.photo:
            image_url = first_photo.photo.url

        first_page_data.append({
            'id': news.id,
            'title': news.title,
            'excerpt': news.short_description,
            'image_url': image_url,
            'published_date': news.publication_date.strftime('%Y-%m-%d'),
            'status': {
                'id': news.info_status.id,
                'name': news.info_status.name,
                'color': get_status_color(news.info_status.name),
                'text_color': get_status_text_color(news.info_status.name),
            },
            'target_direction': {
                'id': news.target_audience.id,
                'name': news.target_audience.name,
            },
            'content_orientation': {
                'id': news.content_type.id,
                'name': news.content_type.name,
            },
        })

    # Подготовка контекста для шаблона
    context = {
        'news': first_page,
        'statuses': info_statuses,
        'target_directions': target_audiences,
        'content_orientations': content_types,
        'current_page': 1,
        'total_pages': paginator.num_pages,

        # JSON для JavaScript с цветами текста
        'statuses_json': json.dumps({
            str(s.id): {
                'id': s.id,
                'name': s.name,
                'color': get_status_color(s.name),
                'text_color': get_status_text_color(s.name),
            } for s in info_statuses
        }, ensure_ascii=False),

        'target_directions_json': json.dumps({
            str(t.id): {
                'id': t.id,
                'name': t.name,
            } for t in target_audiences
        }, ensure_ascii=False),

        'content_orientations_json': json.dumps({
            str(c.id): {
                'id': c.id,
                'name': c.name,
            } for c in content_types
        }, ensure_ascii=False),

        # Добавляем JSON с новостями для первой загрузки
        'news_json': json.dumps(first_page_data, ensure_ascii=False),
    }

    return render(request, 'news/news.html', context)


def news_list_api(request):
    """
    API для AJAX-запросов.
    Возвращает JSON с отфильтрованными новостями.
    """

    # Получаем параметры из GET-запроса
    page = request.GET.get('page', 1)
    sort = request.GET.get('sort', '-publication_date')

    # Получаем фильтры (могут быть множественными)
    status_filter = request.GET.getlist('status[]')
    target_filter = request.GET.getlist('target[]')
    content_filter = request.GET.getlist('content[]')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    # Базовый запрос
    news_queryset = News.objects.filter(is_published=True).select_related(
        'target_audience', 'content_type', 'info_status'
    ).prefetch_related('photos')

    # Применяем фильтры
    if status_filter:
        news_queryset = news_queryset.filter(info_status_id__in=status_filter)

    if target_filter:
        news_queryset = news_queryset.filter(target_audience_id__in=target_filter)

    if content_filter:
        news_queryset = news_queryset.filter(content_type_id__in=content_filter)

    if date_from:
        news_queryset = news_queryset.filter(publication_date__gte=date_from)

    if date_to:
        news_queryset = news_queryset.filter(publication_date__lte=date_to)

    # Применяем сортировку
    sort_mapping = {
        'date-desc': '-publication_date',
        'date-asc': 'publication_date',
        'title-asc': 'title',
        'title-desc': '-title',
    }
    order_by = sort_mapping.get(sort, '-publication_date')
    news_queryset = news_queryset.order_by(order_by)

    # Пагинация
    paginator = Paginator(news_queryset, 9)
    current_page = paginator.get_page(page)

    # Формируем данные для JSON
    news_data = []
    for news in current_page:
        # Получаем первое фото
        first_photo = news.photos.first()
        image_url = None
        if first_photo and first_photo.photo:
            image_url = first_photo.photo.url

        news_data.append({
            'id': news.id,
            'title': news.title,
            'excerpt': news.short_description,
            'image_url': image_url,
            'published_date': news.publication_date.strftime('%Y-%m-%d'),
            'status': {
                'id': news.info_status.id,
                'name': news.info_status.name,
                'color': get_status_color(news.info_status.name),
                'text_color': get_status_text_color(news.info_status.name),
            },
            'target_direction': {
                'id': news.target_audience.id,
                'name': news.target_audience.name,
            },
            'content_orientation': {
                'id': news.content_type.id,
                'name': news.content_type.name,
            },
        })

    # Возвращаем JSON-ответ
    return JsonResponse({
        'news': news_data,
        'total_pages': paginator.num_pages,
        'current_page': int(page),
        'has_next': current_page.has_next(),
        'has_previous': current_page.has_previous(),
        'total_items': paginator.count,
    })


def news_detail(request, news_id):
    """
    Детальная страница новости
    """
    # Получаем новость по ID или возвращаем 404
    news = get_object_or_404(News, id=news_id, is_published=True)

    # Получаем все фото новости (максимум 3)
    all_photos = news.photos.all().order_by('id')
    photos = list(all_photos[:3])

    # Получаем цвета для отображения
    status_color = get_status_color(news.info_status.name)
    status_text_color = get_status_text_color(news.info_status.name)

    # Форматируем дату
    formatted_date = news.publication_date.strftime('%d.%m.%Y')

    # Разбиваем подробное описание на абзацы (если есть)
    description_paragraphs = news.detailed_description.split('\n\n') if news.detailed_description else [news.detailed_description]

    context = {
        'news': news,
        'photos': photos,
        'status_color': status_color,
        'status_text_color': status_text_color,
        'formatted_date': formatted_date,
        'description_paragraphs': description_paragraphs,
        'photos_count': len(photos),
        'has_photos': len(photos) > 0,
    }

    return render(request, 'news/news_detail.html', context)