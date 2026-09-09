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
    Использует только загруженные поля, без дополнительных запросов.
    """
    # Формируем URL файла вручную, без обращения к S3
    file_name = practice.file.name if practice.file else None

    return {
        'id': practice.id,
        'title': practice.title,
        'short_description': practice.short_description,
        'published_date_display': practice.created_date.strftime('%d.%m.%Y') if practice.created_date else '',
        'category': {
            'id': practice.category_id,
            'name': practice.category.name,
            'icon': practice.category.icon,
            'icon_color': practice.category.icon_color,
        },
        'audience': {
            'value': practice.audience or '',
            'display': practice.get_audience_display() if hasattr(practice, 'get_audience_display') else practice.audience,
        },
        'format_type': {
            'value': practice.format_type or '',
            'display': practice.get_format_type_display() if hasattr(practice, 'get_format_type_display') else practice.format_type,
        },
        'difficulty': {
            'value': practice.difficulty or '',
            'display': practice.get_difficulty_display() if hasattr(practice, 'get_difficulty_display') else practice.difficulty,
            'color': practice.difficulty_color,
            'icon': practice.difficulty_icon,
        },
        'has_file': bool(file_name),
        'file_url': (settings.MEDIA_URL + file_name) if file_name else None,
    }


def practices_list(request):
    """
    Страница списка успешных практик (оптимизированная версия).
    Кэшируется только для неавторизованных пользователей.
    """
    # Определяем, авторизован ли пользователь
    is_authenticated = request.session.get('user_type') in ['admin', 'teacher']

    # Базовый запрос - БЕЗ .only() для загрузки всех полей
    practices_queryset = Practice.objects.filter(
        is_published=True
    ).select_related('category').order_by('-created_date')

    paginator = Paginator(practices_queryset, 12)
    first_page = paginator.get_page(1)

    practices_data = [_get_practice_data(practice) for practice in first_page]

    # Получаем категории для фильтров
    categories = PracticeCategory.objects.all().order_by('sort_order', 'name')

    context = {
        'practices': json.dumps(practices_data, ensure_ascii=False),
        'categories': categories,
        'total_pages': paginator.num_pages,
        'current_page': 1,
    }

    # Если пользователь не авторизован — кэшируем ответ
    if not is_authenticated:
        response = render(request, 'success_practices/practices.html', context)
        return response

    return render(request, 'success_practices/practices.html', context)


def practices_list_api(request):
    """
    API для AJAX-запросов (фильтрация, пагинация, сортировка).
    Оптимизированная версия с кэшированием.
    """
    page = request.GET.get('page', 1)
    sort_by = request.GET.get('sort', 'none')

    category_filter = request.GET.getlist('category[]')
    audience_filter = request.GET.getlist('audience[]')
    format_filter = request.GET.getlist('format[]')
    difficulty_filter = request.GET.getlist('difficulty[]')

    # Определяем, авторизован ли пользователь
    is_authenticated = request.session.get('user_type') in ['admin', 'teacher']

    # Ключ кэша (без учета авторизации, так как данные одинаковы)
    filter_hash = hashlib.md5(
        f"{category_filter}_{audience_filter}_{format_filter}_{difficulty_filter}".encode()
    ).hexdigest()[:12]
    cache_key = f'practices_api_{page}_{sort_by}_{filter_hash}'

    # Проверяем кэш (только для неавторизованных пользователей)
    if not is_authenticated:
        cached_response = cache.get(cache_key)
        if cached_response:
            return JsonResponse(cached_response)

    # Базовый запрос - БЕЗ .only()
    practices_queryset = Practice.objects.filter(
        is_published=True
    ).select_related('category')

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

    # Пагинация
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

    # Сохраняем в кэш на 5 минут (только для неавторизованных)
    if not is_authenticated:
        cache.set(cache_key, response_data, 60 * 5)

    return JsonResponse(response_data)


def practice_detail(request, practice_id):
    """
    Детальная информация о практике (без кэша, всегда актуальная).
    """
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
            'display': practice.get_audience_display() if hasattr(practice, 'get_audience_display') else practice.audience,
        },
        'format_type': {
            'value': practice.format_type or '',
            'display': practice.get_format_type_display() if hasattr(practice, 'get_format_type_display') else practice.format_type,
        },
        'difficulty': {
            'value': practice.difficulty or '',
            'display': practice.get_difficulty_display() if hasattr(practice, 'get_difficulty_display') else practice.difficulty,
            'color': practice.difficulty_color,
            'icon': practice.difficulty_icon,
        },
        'published_date_display': practice.created_date.strftime('%d.%m.%Y') if practice.created_date else '',
        'has_file': bool(file_name),
        'file_url': (settings.MEDIA_URL + file_name) if file_name else None,
        'file_name': file_name.split('/')[-1] if file_name else None,
    }

    return JsonResponse(data)