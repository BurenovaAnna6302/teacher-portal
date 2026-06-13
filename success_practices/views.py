from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from django.core.cache import cache
from django.conf import settings
import json
import hashlib
from .models import Practice, PracticeCategory


def _get_practice_data(practice):
    """
    Оптимизированное получение данных практики.
    ИЗБЕГАЕМ обращения к S3 через practice.file.url!
    """
    # practice.file.name — это просто строка из БД (путь к файлу)
    # practice.file — это FileField, обращение к .url делает запрос к S3
    file_name = practice.file.name if practice.file else None

    return {
        'id': practice.id,
        'title': practice.title,
        'short_description': practice.short_description,
        'published_date_display': practice.published_date_display,
        'category': {
            'id': practice.category_id,
            'name': practice.category.name,
            'icon': practice.category.icon,
            'icon_color': practice.category.icon_color,
        },
        'audience': {
            'value': practice.audience or '',
            'display': practice.audience_display,
        },
        'format_type': {
            'value': practice.format_type or '',
            'display': practice.format_display,
        },
        'difficulty': {
            'value': practice.difficulty or '',
            'display': practice.difficulty_display,
            'color': practice.difficulty_color,
            'icon': practice.difficulty_icon,
        },
        # ИСПРАВЛЕНО: формируем URL вручную, без обращения к S3
        'has_file': bool(file_name),
        'file_url': (settings.MEDIA_URL + file_name) if file_name else None,
    }


@cache_page(60 * 15)  # Кэш на 15 минут
def practices_list(request):
    """Страница списка успешных практик (с кэшем)"""
    categories = PracticeCategory.objects.all().order_by('sort_order', 'name')

    # ИСПРАВЛЕНО: убран 'file_id' — его не существует у FileField
    practices_queryset = Practice.objects.filter(
        is_published=True
    ).select_related('category').only(
        'id', 'title', 'short_description', 'created_date',
        'category_id', 'category__name', 'category__icon', 'category__icon_color',
        'audience', 'format_type', 'difficulty', 'file'
    ).order_by('-created_date')

    paginator = Paginator(practices_queryset, 12)
    first_page = paginator.get_page(1)

    practices_data = [_get_practice_data(practice) for practice in first_page]

    context = {
        'practices': json.dumps(practices_data, ensure_ascii=False),
        'categories': categories,
        'total_pages': paginator.num_pages,
        'current_page': 1,
    }

    return render(request, 'success_practices/practices.html', context)


def practices_list_api(request):
    """API для AJAX-запросов (фильтрация, пагинация, сортировка) с кэшем"""
    page = request.GET.get('page', 1)
    sort_by = request.GET.get('sort', 'none')

    category_filter = request.GET.getlist('category[]')
    audience_filter = request.GET.getlist('audience[]')
    format_filter = request.GET.getlist('format[]')
    difficulty_filter = request.GET.getlist('difficulty[]')

    # Используем hashlib для детерминированного ключа кэша
    filter_hash = hashlib.md5(
        f"{category_filter}_{audience_filter}_{format_filter}_{difficulty_filter}".encode()
    ).hexdigest()[:12]

    cache_key = f'practices_api_{page}_{sort_by}_{filter_hash}'

    # Проверяем кэш
    cached_response = cache.get(cache_key)
    if cached_response:
        return JsonResponse(cached_response)

    # ИСПРАВЛЕНО: убран 'file_id'
    practices_queryset = Practice.objects.filter(
        is_published=True
    ).select_related('category').only(
        'id', 'title', 'short_description', 'created_date',
        'category_id', 'category__name', 'category__icon', 'category__icon_color',
        'audience', 'format_type', 'difficulty', 'file'
    )

    # Фильтрация
    if category_filter:
        practices_queryset = practices_queryset.filter(category_id__in=category_filter)
    if audience_filter:
        practices_queryset = practices_queryset.filter(audience__in=audience_filter)
    if format_filter:
        practices_queryset = practices_queryset.filter(format_type__in=format_filter)
    if difficulty_filter:
        practices_queryset = practices_queryset.filter(difficulty__in=difficulty_filter)

    # Сортировка
    sort_mapping = {
        'date-desc': '-created_date',
        'date-asc': 'created_date',
        'title-asc': 'title',
        'title-desc': '-title',
    }
    order_field = sort_mapping.get(sort_by, '-created_date')
    practices_queryset = practices_queryset.order_by(order_field)

    paginator = Paginator(practices_queryset, 12)
    try:
        current_page = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        current_page = paginator.page(1)

    practices_data = [_get_practice_data(practice) for practice in current_page]

    response_data = {
        'practices': practices_data,
        'total_pages': paginator.num_pages,
        'current_page': int(page),
        'has_next': current_page.has_next(),
        'has_previous': current_page.has_previous(),
        'total_items': paginator.count,
    }

    # Сохраняем в кэш на 5 минут
    cache.set(cache_key, response_data, 60 * 5)

    return JsonResponse(response_data)


def practice_detail(request, practice_id):
    """Детальная информация о практике (без кэша)"""
    practice = get_object_or_404(Practice, id=practice_id, is_published=True)

    # Формируем URL вручную, без обращения к S3
    file_name = practice.file.name if practice.file else None

    data = {
        'id': practice.id,
        'title': practice.title,
        'full_description': practice.full_description,
        'short_description': practice.short_description,
        'category': {
            'name': practice.category.name,
            'icon': practice.category.icon,
            'icon_color': practice.category.icon_color,
        },
        'audience': {
            'value': practice.audience or '',
            'display': practice.audience_display,
        },
        'format_type': {
            'value': practice.format_type or '',
            'display': practice.format_display,
        },
        'difficulty': {
            'value': practice.difficulty or '',
            'display': practice.difficulty_display,
            'color': practice.difficulty_color,
            'icon': practice.difficulty_icon,
        },
        'published_date_display': practice.published_date_display,
        'has_file': bool(file_name),
        'file_url': (settings.MEDIA_URL + file_name) if file_name else None,
        'file_name': file_name.split('/')[-1] if file_name else None,
    }

    return JsonResponse(data)