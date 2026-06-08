from django.shortcuts import render
from django.core.paginator import Paginator
from django.http import JsonResponse
import json
from datetime import datetime
from .models import Document, DocumentCategory, ActionLevel


def documents_list(request):
    """
    Страница списка нормативных документов - только первая загрузка.
    """

    # Получаем все справочники из БД
    categories = DocumentCategory.objects.all()
    levels = ActionLevel.objects.all()

    # Получаем только первую страницу документов
    documents_queryset = Document.objects.filter(is_published=True).select_related(
        'category', 'level'
    ).order_by('-publication_date')

    paginator = Paginator(documents_queryset, 8)
    first_page = paginator.get_page(1)

    # Получаем уникальные годы для фильтра
    years_list = Document.objects.filter(is_published=True).dates('publication_date', 'year')
    years_data = []
    for year_date in years_list:
        year_str = str(year_date.year)
        years_data.append({'id': year_str, 'name': year_str})
    # Добавляем "2020 и ранее"
    years_data.append({'id': 'old', 'name': '2020 и ранее'})

    # Подготовка данных для первой страницы (для JavaScript)
    first_page_data = []
    for doc in first_page:
        first_page_data.append({
            'id': doc.id,
            'title': doc.title,
            'description': doc.description,
            'year': doc.year,
            'date': doc.date_display,
            'file_size': doc.file_size_display,
            'file_url': doc.file.url if doc.file else None,
            'category': {
                'id': doc.category.id,
                'name': doc.category.name,
                'bg_color': doc.category.bg_color,
                'text_color': doc.category.text_color,
            },
            'level': {
                'id': doc.level.id,
                'name': doc.level.name,
            },
        })

    # Подготовка контекста
    context = {
        'documents': first_page,
        'categories': categories,
        'levels': levels,
        'years': years_data,
        'current_page': 1,
        'total_pages': paginator.num_pages,
        'has_previous': first_page.has_previous(),
        'has_next': first_page.has_next(),

        # JSON для JavaScript
        'categories_json': json.dumps({
            str(c.id): {
                'id': c.id,
                'name': c.name,
                'bg_color': c.bg_color,
                'text_color': c.text_color,
            } for c in categories
        }, ensure_ascii=False),

        'levels_json': json.dumps({
            str(l.id): {
                'id': l.id,
                'name': l.name,
            } for l in levels
        }, ensure_ascii=False),

        'years_json': json.dumps({
            str(i): y for i, y in enumerate(years_data)
        }, ensure_ascii=False),

        'documents_json': json.dumps(first_page_data, ensure_ascii=False),
    }

    return render(request, 'documents/documents.html', context)


def documents_list_api(request):
    """
    API для AJAX-запросов.
    Возвращает JSON с отфильтрованными документами.
    """

    # Получаем параметры из GET-запроса
    page = request.GET.get('page', 1)

    # Получаем фильтры (без [] в имени параметра)
    category_filter = request.GET.getlist('category')
    level_filter = request.GET.getlist('level')
    year_filter = request.GET.getlist('year')

    print(f"API получил фильтры: category={category_filter}, level={level_filter}, year={year_filter}")

    # Базовый запрос
    documents_queryset = Document.objects.filter(is_published=True).select_related(
        'category', 'level'
    )

    # Применяем фильтры
    if category_filter:
        documents_queryset = documents_queryset.filter(category_id__in=category_filter)

    if level_filter:
        documents_queryset = documents_queryset.filter(level_id__in=level_filter)

    # Фильтр по годам
    if year_filter:
        regular_years = []
        include_old = False

        for year_id in year_filter:
            if year_id == 'old':
                include_old = True
            else:
                regular_years.append(int(year_id))

        from django.db.models import Q
        query = Q()

        if regular_years:
            query |= Q(publication_date__year__in=regular_years)

        if include_old:
            query |= Q(publication_date__year__lte=2020)

        documents_queryset = documents_queryset.filter(query)

    # Сортировка по дате (новые сверху)
    documents_queryset = documents_queryset.order_by('-publication_date')

    # Пагинация
    paginator = Paginator(documents_queryset, 8)
    current_page = paginator.get_page(page)

    # Формируем данные для JSON
    documents_data = []
    for doc in current_page:
        documents_data.append({
            'id': doc.id,
            'title': doc.title,
            'description': doc.description,
            'year': doc.year,
            'date': doc.date_display,
            'file_size': doc.file_size_display,
            'file_url': doc.file.url if doc.file else None,
            'category': {
                'id': doc.category.id,
                'name': doc.category.name,
                'bg_color': doc.category.bg_color,
                'text_color': doc.category.text_color,
            },
            'level': {
                'id': doc.level.id,
                'name': doc.level.name,
            },
        })

    return JsonResponse({
        'documents': documents_data,
        'total_pages': paginator.num_pages,
        'current_page': int(page),
        'has_next': current_page.has_next(),
        'has_previous': current_page.has_previous(),
        'total_items': paginator.count,
    })