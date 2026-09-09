from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.conf import settings
import json
from .models import Practice, PracticeCategory


def _get_practice_data(practice):
    """
    Оптимизированное получение данных практики.
    НЕ ТРОГАЕТ поле file, чтобы избежать обращений к S3!
    """
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
            'color': practice.DIFFICULTY_COLORS.get(practice.difficulty, '#6b7280'),
            'icon': practice.DIFFICULTY_ICONS.get(practice.difficulty, 'fas fa-chart-line'),
        },
        # === ФАЙЛЫ НЕ ЗАГРУЖАЕМ ЗДЕСЬ ===
    }


def practices_list(request):
    """
    Страница списка успешных практик — БЫСТРАЯ, без файлов
    """
    # НЕ ЗАГРУЖАЕМ ПОЛЕ file!
    practices_queryset = Practice.objects.filter(
        is_published=True
    ).select_related('category').defer('file').order_by('-created_date')

    paginator = Paginator(practices_queryset, 12)
    first_page = paginator.get_page(1)

    practices_data = [_get_practice_data(practice) for practice in first_page]
    categories = PracticeCategory.objects.all().order_by('sort_order', 'name')

    context = {
        'practices': json.dumps(practices_data, ensure_ascii=False),
        'categories': categories,
        'total_pages': paginator.num_pages,
        'current_page': 1,
    }

    return render(request, 'success_practices/practices.html', context)


def practices_list_api(request):
    """
    API для AJAX-запросов (фильтрация, пагинация, сортировка) — БЫСТРО, без файлов
    """
    page = request.GET.get('page', 1)
    sort_by = request.GET.get('sort', 'none')

    category_filter = request.GET.getlist('category[]')
    audience_filter = request.GET.getlist('audience[]')
    format_filter = request.GET.getlist('format[]')
    difficulty_filter = request.GET.getlist('difficulty[]')

    # НЕ ЗАГРУЖАЕМ ПОЛЕ file!
    practices_queryset = Practice.objects.filter(
        is_published=True
    ).select_related('category').defer('file')

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
    practices_queryset = practices_queryset.order_by(sort_mapping.get(sort_by, '-created_date'))

    # Пагинация
    paginator = Paginator(practices_queryset, 12)
    try:
        current_page = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        current_page = paginator.page(1)

    practices_data = [_get_practice_data(practice) for practice in current_page]

    return JsonResponse({
        'practices': practices_data,
        'total_pages': paginator.num_pages,
        'current_page': int(page),
        'has_next': current_page.has_next(),
        'has_previous': current_page.has_previous(),
        'total_items': paginator.count,
    })


def practice_detail(request, practice_id):
    """
    Детальная информация о практике — загружаем файлы ТОЛЬКО ЗДЕСЬ
    """
    practice = get_object_or_404(Practice, id=practice_id, is_published=True)

    # ТОЛЬКО ЗДЕСЬ обращаемся к файлу — один раз для конкретной практики
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
            'color': practice.DIFFICULTY_COLORS.get(practice.difficulty, '#6b7280'),
            'icon': practice.DIFFICULTY_ICONS.get(practice.difficulty, 'fas fa-chart-line'),
        },
        'published_date_display': practice.created_date.strftime('%d.%m.%Y') if practice.created_date else '',
        'has_file': bool(file_name),
        'file_url': (settings.MEDIA_URL + file_name) if file_name else None,
        'file_name': file_name.split('/')[-1] if file_name else None,
    }

    return JsonResponse(data)