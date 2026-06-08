from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.http import JsonResponse
import json
import re
from datetime import datetime
from .models import Event, TargetAudience, EventFormat, ActivityType, Subject, EventPhoto


def get_activity_color(activity_name):
    """Возвращает цвет для типа активности"""
    colors = {
        'Вебинар': 'rgba(201, 228, 202, 0.85)',
        'Конкурс': 'rgba(184, 212, 232, 0.85)',
        'Конференция': 'rgba(232, 212, 240, 0.85)',
        'Круглый стол': 'rgba(245, 213, 184, 0.85)',
        'Курсы повышения квалификации': 'rgba(212, 232, 240, 0.85)',
        'Мастер-класс': 'rgba(240, 232, 212, 0.85)',
        'Олимпиада': 'rgba(201, 228, 202, 0.85)',
        'Открытый урок': 'rgba(184, 212, 232, 0.85)',
        'Семинар': 'rgba(232, 212, 240, 0.85)',
        'Слет': 'rgba(245, 213, 184, 0.85)',
        'Тренинг': 'rgba(212, 232, 240, 0.85)',
        'Форум': 'rgba(240, 232, 212, 0.85)',
    }
    return colors.get(activity_name, 'rgba(200, 200, 200, 0.85)')


def get_text_color_for_activity(activity_name):
    """Возвращает яркий цвет текста для типа активности"""
    text_colors = {
        'Вебинар': '#1e8c1e',  # темно-зеленый
        'Конкурс': '#0c4a6e',  # темно-синий
        'Конференция': '#6b21a8',  # темно-фиолетовый
        'Круглый стол': '#c2410c',  # оранжевый
        'Курсы повышения квалификации': '#075985',  # синий
        'Мастер-класс': '#854d0e',  # коричневый
        'Олимпиада': '#1e8c1e',  # темно-зеленый
        'Открытый урок': '#0c4a6e',  # темно-синий
        'Семинар': '#6b21a8',  # темно-фиолетовый
        'Слет': '#c2410c',  # оранжевый
        'Тренинг': '#075985',  # синий
        'Форум': '#854d0e',  # коричневый
    }
    return text_colors.get(activity_name, '#000000')


def events_list(request):

    # Получаем все справочники из БД
    audiences = TargetAudience.objects.all()
    formats = EventFormat.objects.all()
    activity_types = ActivityType.objects.all()
    subjects = Subject.objects.all()

    # Добавляем цвета к типам активности
    for activity in activity_types:
        activity.color = get_activity_color(activity.name)
        activity.text_color = get_text_color_for_activity(activity.name)

    # Получаем только первую страницу мероприятий
    events_queryset = Event.objects.filter(is_published=True).select_related(
        'target_audience', 'format', 'activity_type', 'subject'
    ).prefetch_related('photos').order_by('date', 'title')

    paginator = Paginator(events_queryset, 12)
    first_page = paginator.get_page(1)

    # Подготовка данных для первой страницы
    first_page_data = []
    for event in first_page:
        first_photo = event.photos.first()
        image_url = None
        if first_photo and first_photo.photo:
            image_url = first_photo.photo.url

        first_page_data.append({
            'id': event.id,
            'title': event.title,
            'description': event.short_description,
            'image_url': image_url,
            'date': event.date.strftime('%Y-%m-%d'),
            'time': event.time.strftime('%H:%M'),
            'location': event.location,
            'participants': event.participants,
            'max_participants': event.max_participants,
            'audience': {
                'id': event.target_audience.id,
                'name': event.target_audience.name,
            },
            'format': {
                'id': event.format.id,
                'name': event.format.name,
            },
            'activity_type': {
                'id': event.activity_type.id,
                'name': event.activity_type.name,
                'color': get_activity_color(event.activity_type.name),
                'text_color': get_text_color_for_activity(event.activity_type.name),
            },
            'subject': {
                'id': event.subject.id,
                'name': event.subject.name,
            },
        })

    # Подготовка контекста
    context = {
        'events': first_page,
        'audiences': audiences,
        'formats': formats,
        'activity_types': activity_types,
        'subjects': subjects,
        'current_page': 1,
        'total_pages': paginator.num_pages,

        # JSON для JavaScript
        'audiences_json': json.dumps({
            str(a.id): {
                'id': a.id,
                'name': a.name,
            } for a in audiences
        }, ensure_ascii=False),

        'formats_json': json.dumps({
            str(f.id): {
                'id': f.id,
                'name': f.name,
            } for f in formats
        }, ensure_ascii=False),

        'activity_types_json': json.dumps({
            str(a.id): {
                'id': a.id,
                'name': a.name,
                'color': get_activity_color(a.name),
                'text_color': get_text_color_for_activity(a.name),
            } for a in activity_types
        }, ensure_ascii=False),

        'subjects_json': json.dumps({
            str(s.id): {
                'id': s.id,
                'name': s.name,
            } for s in subjects
        }, ensure_ascii=False),

        'events_json': json.dumps(first_page_data, ensure_ascii=False),
    }

    return render(request, 'events/events.html', context)


def events_list_api(request):
    """
    API для AJAX-запросов мероприятий.
    """

    # Получаем параметры
    page = request.GET.get('page', 1)
    sort = request.GET.get('sort', 'all')

    # Получаем фильтры
    audience_filter = request.GET.getlist('audience[]')
    format_filter = request.GET.getlist('format[]')
    activity_filter = request.GET.getlist('activity_type[]')
    subject_filter = request.GET.getlist('subject[]')

    # Базовый запрос
    events_queryset = Event.objects.filter(is_published=True).select_related(
        'target_audience', 'format', 'activity_type', 'subject'
    ).prefetch_related('photos')

    # Применяем фильтры
    if audience_filter:
        events_queryset = events_queryset.filter(target_audience_id__in=audience_filter)

    if format_filter:
        events_queryset = events_queryset.filter(format_id__in=format_filter)

    if activity_filter:
        events_queryset = events_queryset.filter(activity_type_id__in=activity_filter)

    if subject_filter:
        events_queryset = events_queryset.filter(subject_id__in=subject_filter)

    # Применяем сортировку
    now = datetime.now().date()

    if sort == 'completed':
        # Завершенные мероприятия (прошедшие)
        events_queryset = events_queryset.filter(date__lt=now).order_by('-date')
    elif sort == 'date-asc':
        # Ближайшие (по возрастанию даты)
        events_queryset = events_queryset.filter(date__gte=now).order_by('date', 'title')
    elif sort == 'date-desc':
        # Дальнейшие (по убыванию даты)
        events_queryset = events_queryset.order_by('-date', 'title')
    elif sort == 'name-asc':
        events_queryset = events_queryset.order_by('title')
    elif sort == 'name-desc':
        events_queryset = events_queryset.order_by('-title')
    elif sort == 'all':
        # Все мероприятия (и будущие, и прошедшие)
        events_queryset = events_queryset.order_by('date', 'title')
    else:
        events_queryset = events_queryset.order_by('date', 'title')

    # Пагинация
    paginator = Paginator(events_queryset, 12)
    current_page = paginator.get_page(page)

    # Формируем данные для JSON
    events_data = []
    for event in current_page:
        first_photo = event.photos.first()
        image_url = None
        if first_photo and first_photo.photo:
            image_url = first_photo.photo.url

        events_data.append({
            'id': event.id,
            'title': event.title,
            'description': event.short_description,
            'image_url': image_url,
            'date': event.date.strftime('%Y-%m-%d'),
            'time': event.time.strftime('%H:%M'),
            'location': event.location,
            'participants': event.participants,
            'max_participants': event.max_participants,
            'audience': {
                'id': event.target_audience.id,
                'name': event.target_audience.name,
            },
            'format': {
                'id': event.format.id,
                'name': event.format.name,
            },
            'activity_type': {
                'id': event.activity_type.id,
                'name': event.activity_type.name,
                'color': get_activity_color(event.activity_type.name),
                'text_color': get_text_color_for_activity(event.activity_type.name),
            },
            'subject': {
                'id': event.subject.id,
                'name': event.subject.name,
            },
        })

    return JsonResponse({
        'events': events_data,
        'total_pages': paginator.num_pages,
        'current_page': int(page),
        'has_next': current_page.has_next(),
        'has_previous': current_page.has_previous(),
        'total_items': paginator.count,
    })


def event_detail(request, event_id):
    """
    Детальная страница мероприятия
    """
    # Получаем мероприятие по ID или возвращаем 404
    event = get_object_or_404(Event, id=event_id, is_published=True)

    # Получаем все фото мероприятия, отсортированные по ID
    all_photos = event.photos.all().order_by('id')
    photos = list(all_photos[:6])  # Максимум 6 фото

    # Получаем цвета для отображения
    activity_color = get_activity_color(event.activity_type.name)
    activity_text_color = get_text_color_for_activity(event.activity_type.name)

    # Форматируем дату и время
    formatted_date = event.date.strftime('%d.%m.%Y')
    formatted_time = event.time.strftime('%H:%M')

    # Проверяем, завершено ли мероприятие
    from django.utils import timezone
    is_completed = event.date < timezone.now().date()

    # Разбиваем подробное описание на абзацы
    description_paragraphs = event.detailed_description.split('\n\n')

    context = {
        'event': event,
        'photos': photos,
        'activity_color': activity_color,
        'activity_text_color': activity_text_color,
        'formatted_date': formatted_date,
        'formatted_time': formatted_time,
        'is_completed': is_completed,
        'description_paragraphs': description_paragraphs,
        'photos_count': len(photos),
        'has_multiple_photos': len(photos) > 1,
    }

    return render(request, 'events/event_detail.html', context)