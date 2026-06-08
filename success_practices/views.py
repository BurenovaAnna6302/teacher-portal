from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from .models import Practice, PracticeCategory
import json


@cache_page(60 * 15)  # Кэш на 15 минут
@vary_on_headers('Cookie')
def practices_list(request):
    """Страница списка успешных практик (с кэшем)"""
    # Кэш для категорий (меняются редко)
    categories = PracticeCategory.objects.all().order_by('sort_order', 'name')

    # Используем .only() для выборки только нужных полей (без full_description)
    practices_queryset = Practice.objects.filter(
        is_published=True
    ).select_related('category').only(
        'id', 'title', 'short_description', 'created_date',
        'category__id', 'category__name', 'category__icon', 'category__icon_color',
        'audience', 'format_type', 'difficulty', 'file'
    ).order_by('-created_date')

    paginator = Paginator(practices_queryset, 12)
    first_page = paginator.get_page(1)

    practices_data = []
    for practice in first_page:
        practices_data.append({
            'id': practice.id,
            'title': practice.title,
            'short_description': practice.short_description,
            # full_description не включаем — подгрузим при открытии модалки
            'published_date_display': practice.published_date_display,
            'category': {
                'id': practice.category.id,
                'name': practice.category.name,
                'icon': practice.category.icon,
                'icon_color': practice.category.icon_color,
            },
            'audience': {
                'value': practice.audience if practice.audience else '',
                'display': practice.audience_display,
            },
            'format_type': {
                'value': practice.format_type if practice.format_type else '',
                'display': practice.format_display,
            },
            'difficulty': {
                'value': practice.difficulty if practice.difficulty else '',
                'display': practice.difficulty_display,
                'color': practice.difficulty_color,
                'icon': practice.difficulty_icon,
            },
            'has_file': bool(practice.file),
            'file_url': practice.file.url if practice.file else None,
        })

    context = {
        'practices': json.dumps(practices_data, ensure_ascii=False),
        'categories': categories,
        'total_pages': paginator.num_pages,
        'current_page': 1,
    }

    return render(request, 'success_practices/practices.html', context)


@cache_page(60 * 5)  # Кэш на 5 минут
@vary_on_headers('Cookie')
def practices_list_api(request):
    """API для AJAX-запросов (фильтрация, пагинация, сортировка) с кэшем"""
    page = request.GET.get('page', 1)
    sort_by = request.GET.get('sort', 'none')

    category_filter = request.GET.getlist('category[]')
    audience_filter = request.GET.getlist('audience[]')
    format_filter = request.GET.getlist('format[]')
    difficulty_filter = request.GET.getlist('difficulty[]')

    # Создаём ключ кэша на основе параметров
    cache_key = f'practices_api_{page}_{sort_by}_{hash(str(category_filter))}_{hash(str(audience_filter))}_{hash(str(format_filter))}_{hash(str(difficulty_filter))}'
    cached_response = cache.get(cache_key)
    if cached_response:
        return JsonResponse(cached_response)

    practices_queryset = Practice.objects.filter(
        is_published=True
    ).select_related('category').only(
        'id', 'title', 'short_description', 'created_date',
        'category__id', 'category__name', 'category__icon', 'category__icon_color',
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
    if sort_by == 'date-desc':
        practices_queryset = practices_queryset.order_by('-created_date')
    elif sort_by == 'date-asc':
        practices_queryset = practices_queryset.order_by('created_date')
    elif sort_by == 'title-asc':
        practices_queryset = practices_queryset.order_by('title')
    elif sort_by == 'title-desc':
        practices_queryset = practices_queryset.order_by('-title')
    else:
        practices_queryset = practices_queryset.order_by('-created_date')

    paginator = Paginator(practices_queryset, 12)
    try:
        current_page = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        current_page = paginator.page(1)

    practices_data = []
    for practice in current_page:
        practices_data.append({
            'id': practice.id,
            'title': practice.title,
            'short_description': practice.short_description,
            'published_date_display': practice.published_date_display,
            'category': {
                'id': practice.category.id,
                'name': practice.category.name,
                'icon': practice.category.icon,
                'icon_color': practice.category.icon_color,
            },
            'audience': {
                'value': practice.audience if practice.audience else '',
                'display': practice.audience_display,
            },
            'format_type': {
                'value': practice.format_type if practice.format_type else '',
                'display': practice.format_display,
            },
            'difficulty': {
                'value': practice.difficulty if practice.difficulty else '',
                'display': practice.difficulty_display,
                'color': practice.difficulty_color,
                'icon': practice.difficulty_icon,
            },
            'has_file': bool(practice.file),
            'file_url': practice.file.url if practice.file else None,
        })

    response_data = {
        'practices': practices_data,
        'total_pages': paginator.num_pages,
        'current_page': int(page),
        'has_next': current_page.has_next(),
        'has_previous': current_page.has_previous(),
        'total_items': paginator.count,
    }

    # Сохраняем в кэш
    cache.set(cache_key, response_data, 60 * 5)  # 5 минут

    return JsonResponse(response_data)


def practice_detail(request, practice_id):
    """Детальная информация о практике (без кэша, т.к. редко запрашивается)"""
    practice = get_object_or_404(Practice, id=practice_id, is_published=True)

    data = {
        'id': practice.id,
        'title': practice.title,
        'full_description': practice.full_description,  # только здесь подгружаем
        'short_description': practice.short_description,
        'category': {
            'name': practice.category.name,
            'icon': practice.category.icon,
            'icon_color': practice.category.icon_color,
        },
        'audience': {
            'value': practice.audience if practice.audience else '',
            'display': practice.audience_display,
        },
        'format_type': {
            'value': practice.format_type if practice.format_type else '',
            'display': practice.format_display,
        },
        'difficulty': {
            'value': practice.difficulty if practice.difficulty else '',
            'display': practice.difficulty_display,
            'color': practice.difficulty_color,
            'icon': practice.difficulty_icon,
        },
        'published_date_display': practice.published_date_display,
        'has_file': bool(practice.file),
        'file_url': practice.file.url if practice.file else None,
        'file_name': practice.file.name.split('/')[-1] if practice.file else None,
    }

    return JsonResponse(data)