from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings
import uuid
from datetime import datetime
import json
import os
from .constants import *

# Импортируем реальные модели из всех приложений
from news.models import News as RealNews
from news.models import TargetAudience, ContentType, InfoStatus, NewsPhoto

from events.models import Event as RealEvent
from events.models import EventFormat, ActivityType, Subject, EventPhoto

from materials.models import Material as RealMaterial
from materials.models import Subject as MaterialSubject
from materials.models import MaterialType, DifficultyLevel, Grade, WorkFormat, AssessmentSystem, AdditionalCategory

from documents.models import Document as RealDocument
from documents.models import DocumentCategory, ActionLevel

from surveys.models import Survey as RealSurvey
from surveys.models import SurveyCategory, ActivityStatus, Question, QuestionType, AnswerOption, SurveyPassing, \
    TeacherAnswer
from surveys.models import Survey, SurveyCategory, ActivityStatus, SurveyPassing

# Временное хранилище в памяти (больше не используется для основных сущностей,
# но оставляем для совместимости)
storage = {
    'events': [],
    'materials': [],
    'documents': [],
    'surveys': [],
    'questions': [],
    'survey_responses': [],
}


# ========== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==========
def _get_storage_item(storage_key, item_id):
    """Получить элемент из хранилища по ID"""
    return next((item for item in storage[storage_key] if item['id'] == item_id), None)


def _update_storage_item(storage_key, item_id, data):
    """Обновить элемент в хранилище"""
    for i, item in enumerate(storage[storage_key]):
        if item['id'] == item_id:
            storage[storage_key][i].update(data)
            return True
    return False


def _delete_storage_item(storage_key, item_id):
    """Удалить элемент из хранилища"""
    storage[storage_key] = [item for item in storage[storage_key] if item['id'] != item_id]


# ========== АУТЕНТИФИКАЦИЯ С ДВУХФАКТОРКОЙ ==========

@csrf_exempt
def check_admin_code(request):
    """
    Проверка секретного кода для двухфакторной аутентификации
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            entered_code = data.get('code', '').strip()

            # Получаем коды из настроек (которые загружены из .env)
            admin_secret_code = getattr(settings, 'ADMIN_SECRET_CODE', '')
            admin_backup_code = getattr(settings, 'ADMIN_BACKUP_CODE', '')

            # Проверяем код из переменных окружения
            if entered_code == admin_secret_code or entered_code == admin_backup_code:
                # Сохраняем в сессии, что код подтвержден
                request.session['admin_code_verified'] = True
                # Устанавливаем время жизни сессии (30 минут)
                request.session.set_expiry(1800)

                return JsonResponse({
                    'success': True,
                    'redirect_url': reverse('admin_panel:admin_login')
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Неверный код доступа'
                })
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Ошибка формата данных'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Ошибка при обработке запроса: {str(e)}'
            })

    return JsonResponse({'success': False, 'error': 'Метод не поддерживается'})


def admin_login(request):
    """Вход в админ-панель (по email и паролю)"""

    if request.session.get('admin_authenticated'):
        return redirect('admin_panel:dashboard')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()

        from admin_panel.models import AdminUser

        try:
            admin_user = AdminUser.objects.get(email=email, is_active=True)

            if admin_user.check_password(password):
                request.session['admin_authenticated'] = True
                request.session['is_admin'] = True  # ← ДОБАВИТЬ ЭТУ СТРОКУ
                request.session['admin_id'] = admin_user.id
                request.session['admin_name'] = admin_user.name
                request.session['admin_email'] = admin_user.email
                return redirect('admin_panel:dashboard')
            else:
                return render(request, 'admin_panel/login.html', {'error': 'Неверный пароль', 'email': email})
        except AdminUser.DoesNotExist:
            return render(request, 'admin_panel/login.html',
                          {'error': 'Администратор с таким email не найден', 'email': email})

    return render(request, 'admin_panel/login.html')

def admin_logout(request):
    """Выход из админки"""
    request.session.flush()
    messages.success(request, 'Вы вышли из системы')
    return redirect('admin_panel:admin_login')

def check_admin_access(request):
    """Проверка доступа к админке"""
    if not request.session.get('admin_authenticated') and not request.session.get('is_admin'):
        messages.error(request, 'Для доступа к админке необходимо войти')
        return False
    return True

# ========== ДАШБОРД (ГЛАВНАЯ) ==========
def dashboard(request):
    """Главная страница админки"""
    if not check_admin_access(request):
        return redirect('admin_panel:admin_login')

    from django.utils import timezone
    now = timezone.now()

    # Получаем события для календаря (без изменения БД)
    month_events = RealEvent.objects.filter(
        date__year=now.year,
        date__month=now.month
    ).values('id', 'title', 'date')

    month_news = RealNews.objects.filter(
        publication_date__year=now.year,
        publication_date__month=now.month
    ).values('id', 'title', 'publication_date')

    month_surveys = RealSurvey.objects.filter(
        deadline__year=now.year,
        deadline__month=now.month
    ).values('id', 'title', 'deadline')

    stats = {
        'events': RealEvent.objects.count(),
        'news': RealNews.objects.count(),
        'materials': RealMaterial.objects.count(),
        'documents': RealDocument.objects.count(),
        'surveys': RealSurvey.objects.count(),
        'questions': Question.objects.count(),
    }

    context = {
        'admin_name': request.session.get('admin_name', 'Администратор'),
        'stats': stats,
        'month_events': month_events,
        'month_news': month_news,
        'month_surveys': month_surveys,
        'page_title': 'Главная'
    }

    return render(request, 'admin_panel/dashboard.html', context)


# ========== СТАТИСТИКА ==========
# В функции statistics(request) нужно исправить подсчет статусов:

def statistics(request):
    """Страница статистики опросов"""
    if not check_admin_access(request):
        return redirect('admin_panel:admin_login')

    # Общая статистика
    total_surveys = RealSurvey.objects.count()

    # Подсчет статусов
    all_statuses = ActivityStatus.objects.all()

    active_surveys = 0
    completed_surveys = 0

    for status in all_statuses:
        status_name_lower = status.name.lower()
        if 'актив' in status_name_lower or 'active' in status_name_lower:
            active_surveys += RealSurvey.objects.filter(status=status).count()
        elif 'заверш' in status_name_lower or 'completed' in status_name_lower:
            completed_surveys += RealSurvey.objects.filter(status=status).count()

    # ИСПРАВЛЕНО: Только общее количество ответов
    total_responses = SurveyPassing.objects.count()

    # Категории для фильтра
    categories = SurveyCategory.objects.all()

    # Список опросов
    surveys_list = []
    for survey in RealSurvey.objects.all().select_related('category', 'status').prefetch_related('questions').order_by(
            '-created_date'):
        # ИСПРАВЛЕНО: Только количество ответов для этого опроса
        responses_count = SurveyPassing.objects.filter(survey=survey).count()

        # Определяем статус для отображения
        status_class = 'draft'
        status_display = 'Черновик'

        if survey.status:
            status_name_lower = survey.status.name.lower()
            if 'актив' in status_name_lower or 'active' in status_name_lower:
                status_class = 'active'
                status_display = 'Активный'
            elif 'заверш' in status_name_lower or 'completed' in status_name_lower:
                status_class = 'completed'
                status_display = 'Завершённый'
            else:
                status_class = 'draft'
                status_display = survey.status.name

        surveys_list.append({
            'id': survey.id,
            'title': survey.title,
            'category_name': survey.category.name if survey.category else 'Без категории',
            'category_id': survey.category.id if survey.category else '',
            'status': status_class,
            'status_display': status_display,
            'responses': responses_count,  # Только ответы
            'questions_count': survey.questions.count(),
        })

    context = {
        'total_surveys': total_surveys,
        'active_surveys': active_surveys,
        'completed_surveys': completed_surveys,
        'total_responses': total_responses,  # Только ответы
        'categories': categories,
        'surveys': surveys_list,
        'admin_name': request.session.get('admin_name', 'Администратор'),
        'page_title': 'Статистика опросов'
    }

    return render(request, 'admin_panel/statistics.html', context)


# ========== ДЕТАЛЬНАЯ СТАТИСТИКА ОПРОСА ==========
def survey_statistics(request, survey_id):
    """Детальная статистика по конкретному опросу"""
    if not check_admin_access(request):
        return redirect('admin_panel:admin_login')

    # Получаем реальный опрос из БД
    try:
        survey = RealSurvey.objects.get(id=survey_id)
    except RealSurvey.DoesNotExist:
        messages.error(request, 'Опрос не найден')
        return redirect('admin_panel:statistics')

    # Получаем все прохождения опроса
    passings = SurveyPassing.objects.filter(survey=survey)
    total_responses = passings.count()  # Только количество ответов, не участников

    # Собираем статистику по вопросам
    questions_stats = []
    for question in survey.questions.all().order_by('order'):
        answers = TeacherAnswer.objects.filter(question=question)

        # Определяем тип вопроса
        question_type_name = question.question_type.name if question.question_type else 'Текстовый ответ'

        question_data = {
            'id': question.id,
            'text': question.text,
            'type': 'single' if question_type_name == 'Одиночный выбор' else
            'multiple' if question_type_name == 'Множественный выбор' else 'text',
            'required': question.is_required,
            'answers_count': answers.count(),
        }

        # Статистика по вариантам для вопросов с выбором
        if question_type_name in ['Одиночный выбор', 'Множественный выбор']:
            options_stats = []
            total_responses_for_question = 0

            for option in question.options.all().order_by('order'):
                if question_type_name == 'Одиночный выбор':
                    count = TeacherAnswer.objects.filter(
                        question=question,
                        selected_option=option
                    ).count()
                else:
                    count = TeacherAnswer.objects.filter(
                        question=question,
                        selected_options=option
                    ).count()

                total_responses_for_question += count
                percentage = round((count / total_responses * 100), 1) if total_responses > 0 else 0
                options_stats.append({
                    'text': option.text,
                    'count': count,
                    'percentage': percentage,
                })

            question_data['options'] = options_stats
            question_data['total_responses'] = total_responses_for_question
        else:
            # Для открытых вопросов собираем текстовые ответы
            text_answers = answers.exclude(text_answer='').values_list('text_answer', flat=True)
            question_data['text_answers'] = list(text_answers)[:20]  # Показываем первые 20
            question_data['text_answers_count'] = len(text_answers)

        questions_stats.append(question_data)

    # Определяем статус для отображения
    if survey.status:
        if survey.status.name == 'Активный':
            status = 'active'
            status_display = 'Активный'
        elif survey.status.name == 'Завершенный':
            status = 'completed'
            status_display = 'Завершённый'
        else:
            status = 'draft'
            status_display = survey.status.name
    else:
        status = 'draft'
        status_display = 'Черновик'

    survey_data = {
        'id': survey.id,
        'title': survey.title,
        'description': survey.description,
        'category': survey.category.name if survey.category else 'Без категории',
        'status': status,
        'status_display': status_display,
        'participants': total_responses,  # Переименовано, но показываем ответы
        'questions': questions_stats,
        'created_at': survey.created_date.strftime('%d.%m.%Y') if survey.created_date else '',
        'duration': survey.duration,
    }

    return render(request, 'admin_panel/survey_statistics.html', {
        'survey': survey_data,
        'admin_name': request.session.get('admin_name', 'Администратор'),
        'page_title': f'Статистика: {survey_data["title"]}'
    })



# ========== МЕРОПРИЯТИЯ ==========
def event_list(request):
    """Список мероприятий из реальной БД"""
    if not check_admin_access(request):
        return redirect('admin_panel:admin_login')

    # Получаем фильтры из GET-параметров
    activity_filter = request.GET.get('activity_type')
    format_filter = request.GET.get('format')
    audience_filter = request.GET.get('audience')
    status_filter = request.GET.get('status')

    # Базовый запрос
    events_queryset = RealEvent.objects.all().select_related(
        'target_audience', 'format', 'activity_type', 'subject'
    ).prefetch_related('photos').order_by('date', 'time')

    # Применяем фильтры
    if activity_filter and activity_filter != '':
        events_queryset = events_queryset.filter(activity_type__name__icontains=activity_filter)

    if format_filter and format_filter != '':
        events_queryset = events_queryset.filter(format__name__icontains=format_filter)

    if audience_filter and audience_filter != '':
        events_queryset = events_queryset.filter(target_audience__name__icontains=audience_filter)

    # Фильтр по статусу (предстоящие/завершенные)
    if status_filter and status_filter != '':
        from django.utils import timezone
        now = timezone.now()
        if status_filter == 'upcoming':
            events_queryset = events_queryset.filter(date__gte=now.date()) | \
                              events_queryset.filter(date=now.date(), time__gte=now.time())
        elif status_filter == 'completed':
            events_queryset = events_queryset.filter(date__lt=now.date()) | \
                              events_queryset.filter(date=now.date(), time__lt=now.time())

    # Пагинация - 8 элементов на страницу
    page = request.GET.get('page', 1)
    paginator = Paginator(events_queryset, 8)

    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    # Получаем все справочники из БД для фильтров
    db_activity_types = ActivityType.objects.all().order_by('name')
    db_formats = EventFormat.objects.all().order_by('name')
    db_audiences = TargetAudience.objects.all().order_by('name')
    db_subjects = Subject.objects.all().order_by('name')

    # Подготавливаем данные для шаблона
    events_data = []
    for event in page_obj:
        # Получаем фото (первое для превью)
        first_photo = event.photos.first()
        photo_url = None
        if first_photo and first_photo.photo:
            photo_url = first_photo.photo.url

        from django.utils import timezone
        now = timezone.now()
        is_upcoming = event.date > now.date() or (event.date == now.date() and event.time > now.time())

        events_data.append({
            'id': event.id,
            'title': event.title,
            'short_description': event.short_description,
            'detailed_description': event.detailed_description,
            'date': event.date.strftime('%Y-%m-%d'),
            'time': event.time.strftime('%H:%M'),
            'date_display': event.date.strftime('%d.%m.%Y'),
            'time_display': event.time.strftime('%H:%M'),
            'location': event.location,
            'participants': event.participants,
            'is_upcoming': is_upcoming,
            'activity_type': {
                'id': event.activity_type.id if event.activity_type else None,
                'name': event.activity_type.name if event.activity_type else 'Не указан',
            },
            'format': {
                'id': event.format.id if event.format else None,
                'name': event.format.name if event.format else 'Не указан',
            },
            'subject': {
                'id': event.subject.id if event.subject else None,
                'name': event.subject.name if event.subject else 'Не указан',
            },
            'target_audience': {
                'id': event.target_audience.id if event.target_audience else None,
                'name': event.target_audience.name if event.target_audience else 'Не указан',
            },
            'photo_url': photo_url,
            'created_at': event.created_at.strftime('%d.%m.%Y %H:%M') if event.created_at else '',
            'updated_at': event.updated_at.strftime('%d.%m.%Y %H:%M') if event.updated_at else '',
        })

    return render(request, 'admin_panel/events/list.html', {
        'events': events_data,
        'page_obj': page_obj,
        'paginator': paginator,
        'activity_types': EVENT_ACTIVITY_TYPES,
        'formats': EVENT_FORMATS,
        'audiences': EVENT_AUDIENCES,
        'subjects': EVENT_SUBJECTS,
        'db_activity_types': db_activity_types,
        'db_formats': db_formats,
        'db_audiences': db_audiences,
        'db_subjects': db_subjects,
        'current_filters': {
            'activity_type': activity_filter if activity_filter else '',
            'format': format_filter if format_filter else '',
            'audience': audience_filter if audience_filter else '',
            'status': status_filter if status_filter else '',
        },
        'page_title': 'Мероприятия',
        'admin_name': request.session.get('admin_name', 'Администратор'),
    })


@csrf_exempt
def event_create(request):
    """Создание мероприятия в реальной БД"""
    if not check_admin_access(request):
        return redirect('admin_panel:admin_login')

    # Получаем реальные справочники из БД
    audiences = TargetAudience.objects.all().order_by('name')
    formats = EventFormat.objects.all().order_by('name')
    activity_types = ActivityType.objects.all().order_by('name')
    subjects = Subject.objects.all().order_by('name')

    if request.method == 'POST':
        try:
            # Получаем данные из формы
            title = request.POST.get('title', '').strip()
            short_description = request.POST.get('short_description', '').strip()
            detailed_description = request.POST.get('full_description', '').strip()
            date_time = request.POST.get('date_time', '')
            location = request.POST.get('location', '').strip()
            subject_id = request.POST.get('subject_area', '')
            activity_type_id = request.POST.get('activity_type', '')
            format_id = request.POST.get('format', '')
            audience_id = request.POST.get('target_audience', '')

            # Валидация
            if not title:
                messages.error(request, 'Название мероприятия обязательно')
                return render(request, 'admin_panel/events/form.html', {
                    'audiences': audiences,
                    'formats': formats,
                    'activity_types': activity_types,
                    'subjects': subjects,
                })

            if not date_time:
                messages.error(request, 'Дата и время проведения обязательны')
                return render(request, 'admin_panel/events/form.html', {
                    'audiences': audiences,
                    'formats': formats,
                    'activity_types': activity_types,
                    'subjects': subjects,
                })

            # Парсим дату и время
            from datetime import datetime
            dt = datetime.strptime(date_time, '%Y-%m-%dT%H:%M')

            # Создаем мероприятие
            event = RealEvent.objects.create(
                title=title,
                short_description=short_description,
                detailed_description=detailed_description,
                date=dt.date(),
                time=dt.time(),
                location=location,
                subject_id=subject_id if subject_id else None,
                activity_type_id=activity_type_id if activity_type_id else None,
                format_id=format_id if format_id else None,
                target_audience_id=audience_id if audience_id else None,
                is_published=True
            )

            # Обработка загруженных фото (максимум 6)
            photos = request.FILES.getlist('photos')
            for i, photo_file in enumerate(photos[:6]):
                EventPhoto.objects.create(
                    event=event,
                    photo=photo_file
                )

            messages.success(request, 'Мероприятие успешно создано')
            return redirect('admin_panel:event_list')

        except Exception as e:
            messages.error(request, f'Ошибка при создании мероприятия: {str(e)}')

    return render(request, 'admin_panel/events/form.html', {
        'audiences': audiences,
        'formats': formats,
        'activity_types': activity_types,
        'subjects': subjects,
        'page_title': 'Создание мероприятия',
        'admin_name': request.session.get('admin_name', 'Администратор'),
    })


@csrf_exempt
def event_edit(request, event_id):
    """Редактирование мероприятия в реальной БД"""
    if not check_admin_access(request):
        return redirect('admin_panel:admin_login')

    # Получаем мероприятие из БД
    event = get_object_or_404(RealEvent, id=event_id)

    # Получаем справочники
    audiences = TargetAudience.objects.all().order_by('name')
    formats = EventFormat.objects.all().order_by('name')
    activity_types = ActivityType.objects.all().order_by('name')
    subjects = Subject.objects.all().order_by('name')

    # Получаем фото мероприятия
    existing_photos = event.photos.all()[:6]

    if request.method == 'POST':
        try:
            # Получаем данные из формы
            title = request.POST.get('title', '').strip()
            short_description = request.POST.get('short_description', '').strip()
            detailed_description = request.POST.get('full_description', '').strip()
            date_time = request.POST.get('date_time', '')
            location = request.POST.get('location', '').strip()
            subject_id = request.POST.get('subject_area', '')
            activity_type_id = request.POST.get('activity_type', '')
            format_id = request.POST.get('format', '')
            audience_id = request.POST.get('target_audience', '')

            # Валидация
            if not title:
                messages.error(request, 'Название мероприятия обязательно')
                return render(request, 'admin_panel/events/form.html', {
                    'event': event,
                    'audiences': audiences,
                    'formats': formats,
                    'activity_types': activity_types,
                    'subjects': subjects,
                    'existing_photos': existing_photos,
                })

            # Парсим дату и время
            from datetime import datetime
            dt = datetime.strptime(date_time, '%Y-%m-%dT%H:%M')

            # Обновляем мероприятие
            event.title = title
            event.short_description = short_description
            event.detailed_description = detailed_description
            event.date = dt.date()
            event.time = dt.time()
            event.location = location
            event.subject_id = subject_id if subject_id else None
            event.activity_type_id = activity_type_id if activity_type_id else None
            event.format_id = format_id if format_id else None
            event.target_audience_id = audience_id if audience_id else None
            event.save()

            # Обработка удаления старых фото
            photos_to_delete = request.POST.getlist('delete_photos')
            for photo_id in photos_to_delete:
                try:
                    photo = EventPhoto.objects.get(id=photo_id, event=event)
                    if photo.photo:
                        if os.path.isfile(photo.photo.path):
                            os.remove(photo.photo.path)
                    photo.delete()
                except EventPhoto.DoesNotExist:
                    pass

            # Обработка новых фото
            new_photos = request.FILES.getlist('photos')
            current_photos_count = event.photos.count()

            for photo_file in new_photos:
                if current_photos_count < 6:
                    EventPhoto.objects.create(
                        event=event,
                        photo=photo_file
                    )
                    current_photos_count += 1
                else:
                    messages.warning(request, 'Максимум 6 фото. Лишние фото не сохранены.')
                    break

            messages.success(request, 'Мероприятие успешно обновлено')
            return redirect('admin_panel:event_list')

        except Exception as e:
            messages.error(request, f'Ошибка при обновлении мероприятия: {str(e)}')

    # Подготавливаем данные для шаблона
    from django.utils import timezone
    now = timezone.now()
    is_upcoming = event.date > now.date() or (event.date == now.date() and event.time > now.time())

    event_data = {
        'id': event.id,
        'title': event.title,
        'short_description': event.short_description,
        'detailed_description': event.detailed_description,
        'date': event.date.strftime('%Y-%m-%d'),
        'time': event.time.strftime('%H:%M'),
        'date_time': f"{event.date.strftime('%Y-%m-%d')}T{event.time.strftime('%H:%M')}",
        'location': event.location,
        'subject_id': event.subject_id,
        'activity_type_id': event.activity_type_id,
        'format_id': event.format_id,
        'target_audience_id': event.target_audience_id,
        'participants': event.participants,
        'is_upcoming': is_upcoming,
        'created_at': event.created_at.strftime('%d.%m.%Y %H:%M') if event.created_at else '',
        'updated_at': event.updated_at.strftime('%d.%m.%Y %H:%M') if event.updated_at else '',
    }

    # Подготавливаем данные о существующих фото
    photos_data = []
    for photo in existing_photos:
        if photo.photo:
            photos_data.append({
                'id': photo.id,
                'url': photo.photo.url,
                'filename': os.path.basename(photo.photo.name),
            })

    return render(request, 'admin_panel/events/form.html', {
        'event': event_data,
        'audiences': audiences,
        'formats': formats,
        'activity_types': activity_types,
        'subjects': subjects,
        'existing_photos': photos_data,
        'page_title': f'Редактирование: {event.title}',
        'admin_name': request.session.get('admin_name', 'Администратор'),
    })


@csrf_exempt
def event_delete(request, event_id):
    """Удаление мероприятия из реальной БД"""
    if not check_admin_access(request):
        return redirect('admin_panel:admin_login')

    if request.method == 'POST':
        event = get_object_or_404(RealEvent, id=event_id)

        # Удаляем связанные фото
        for photo in event.photos.all():
            if photo.photo:
                if os.path.isfile(photo.photo.path):
                    os.remove(photo.photo.path)
            photo.delete()

        event.delete()
        messages.success(request, 'Мероприятие успешно удалено')

    return redirect('admin_panel:event_list')


# ========== НОВОСТИ ==========
def news_list(request):
    """Список новостей из реальной БД"""
    if not check_admin_access(request):
        return redirect('admin_panel:admin_login')

    # Получаем фильтры из GET-параметров
    status_filter = request.GET.get('status')
    content_type_filter = request.GET.get('content_type')
    audience_filter = request.GET.get('audience')

    # Базовый запрос
    news_queryset = RealNews.objects.all().select_related(
        'target_audience', 'content_type', 'info_status'
    ).prefetch_related('photos')

    # Применяем фильтры
    if status_filter and status_filter != '':
        news_queryset = news_queryset.filter(info_status__name__icontains=status_filter)

    if content_type_filter and content_type_filter != '':
        news_queryset = news_queryset.filter(content_type__name__icontains=content_type_filter)

    if audience_filter and audience_filter != '':
        news_queryset = news_queryset.filter(target_audience__name__icontains=audience_filter)

    # Сортировка
    news_queryset = news_queryset.order_by('-publication_date', '-created_at')

    # Пагинация - 8 элементов на страницу
    page = request.GET.get('page', 1)
    paginator = Paginator(news_queryset, 8)

    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    # Получаем все справочники из БД для фильтров
    db_statuses = InfoStatus.objects.all().order_by('name')
    db_content_types = ContentType.objects.all().order_by('name')
    db_target_audiences = TargetAudience.objects.all().order_by('name')

    # Подготавливаем данные для шаблона
    news_data = []
    for news in page_obj:
        # Получаем фото (макс 3)
        photos = news.photos.all()[:3]
        photos_data = []
        for photo in photos:
            if photo.photo:
                photos_data.append({
                    'id': photo.id,
                    'url': photo.photo.url
                })

        # Находим соответствующие значения из констант для отображения
        status_value = news.info_status.name.lower().replace(' ', '_') if news.info_status else 'unknown'
        content_value = news.content_type.name.lower().replace(' ', '_') if news.content_type else 'unknown'
        audience_value = news.target_audience.name.lower().replace(' ', '_') if news.target_audience else 'unknown'

        news_data.append({
            'id': news.id,
            'title': news.title,
            'short_description': news.short_description,
            'detailed_description': news.detailed_description,
            'publish_date': news.publication_date.strftime('%Y-%m-%d'),
            'publish_date_display': news.publication_date.strftime('%d.%m.%Y'),
            'status': {
                'id': news.info_status.id if news.info_status else None,
                'name': news.info_status.name if news.info_status else 'Не указан',
                'value': status_value,
                'color': next((s['color'] for s in NEWS_STATUSES if s['value'] == status_value),
                              'rgba(200,200,200,0.85)'),
                'text_color': next((s['text_color'] for s in NEWS_STATUSES if s['value'] == status_value), '#000000'),
            },
            'content_type': {
                'id': news.content_type.id if news.content_type else None,
                'name': news.content_type.name if news.content_type else 'Не указан',
                'value': content_value,
            },
            'target_audience': {
                'id': news.target_audience.id if news.target_audience else None,
                'name': news.target_audience.name if news.target_audience else 'Не указан',
                'value': audience_value,
                'color': next((a['color'] for a in NEWS_TARGET_AUDIENCES if a['value'] == audience_value),
                              'rgba(200,200,200,0.85)'),
            },
            'is_published': news.is_published,
            'created_at': news.created_at.strftime('%d.%m.%Y %H:%M') if news.created_at else '',
            'updated_at': news.updated_at.strftime('%d.%m.%Y %H:%M') if news.updated_at else '',
            'photos': photos_data,
            'photos_count': len(photos_data),
        })

    return render(request, 'admin_panel/news/list.html', {
        'news': news_data,
        'page_obj': page_obj,
        'paginator': paginator,
        'statuses': NEWS_STATUSES,
        'target_audiences': NEWS_TARGET_AUDIENCES,
        'content_types': NEWS_CONTENT_TYPES,
        'db_statuses': db_statuses,
        'db_content_types': db_content_types,
        'db_target_audiences': db_target_audiences,
        'current_filters': {
            'status': status_filter if status_filter else '',
            'content_type': content_type_filter if content_type_filter else '',
            'audience': audience_filter if audience_filter else '',
        },
        'page_title': 'Новости',
        'admin_name': request.session.get('admin_name', 'Администратор'),
    })


@csrf_exempt
def news_create(request):
    """Создание новости в реальной БД"""
    if not check_admin_access(request):
        return redirect('admin_panel:admin_login')

    # Получаем реальные справочники из БД
    target_audiences = TargetAudience.objects.all().order_by('name')
    content_types = ContentType.objects.all().order_by('name')
    info_statuses = InfoStatus.objects.all().order_by('name')

    if request.method == 'POST':
        try:
            # Получаем данные из формы
            title = request.POST.get('title', '').strip()
            short_description = request.POST.get('short_description', '').strip()
            detailed_description = request.POST.get('detailed_description', '').strip()
            publish_date = request.POST.get('publish_date', '')
            status_id = request.POST.get('status', '')
            content_type_id = request.POST.get('content_type', '')
            target_audience_id = request.POST.get('target_audience', '')

            # Валидация
            if not title:
                messages.error(request, 'Заголовок новости обязателен')
                return render(request, 'admin_panel/news/form.html', {
                    'target_audiences': target_audiences,
                    'content_types': content_types,
                    'info_statuses': info_statuses,
                })

            if not status_id:
                messages.error(request, 'Статус информации обязателен')
                return render(request, 'admin_panel/news/form.html', {
                    'target_audiences': target_audiences,
                    'content_types': content_types,
                    'info_statuses': info_statuses,
                })

            # Создаем новость
            from django.utils import timezone
            news = RealNews.objects.create(
                title=title,
                short_description=short_description,
                detailed_description=detailed_description,
                publication_date=publish_date or timezone.now().date(),
                target_audience_id=target_audience_id if target_audience_id else None,
                content_type_id=content_type_id if content_type_id else None,
                info_status_id=status_id,
                is_published=True
            )

            # Обработка загруженных фото (максимум 3)
            photos = request.FILES.getlist('photos')
            for i, photo_file in enumerate(photos[:3]):
                NewsPhoto.objects.create(
                    news=news,
                    photo=photo_file
                )

            messages.success(request, 'Новость успешно создана')
            return redirect('admin_panel:news_list')

        except Exception as e:
            messages.error(request, f'Ошибка при создании новости: {str(e)}')

    return render(request, 'admin_panel/news/form.html', {
        'target_audiences': target_audiences,
        'content_types': content_types,
        'info_statuses': info_statuses,
        'page_title': 'Создание новости',
        'admin_name': request.session.get('admin_name', 'Администратор'),
    })


@csrf_exempt
def news_edit(request, news_id):
    """Редактирование новости в реальной БД"""
    if not check_admin_access(request):
        return redirect('admin_panel:admin_login')

    # Получаем новость из БД
    news = get_object_or_404(RealNews, id=news_id)

    # Получаем справочники
    target_audiences = TargetAudience.objects.all().order_by('name')
    content_types = ContentType.objects.all().order_by('name')
    info_statuses = InfoStatus.objects.all().order_by('name')

    # Получаем фото новости
    existing_photos = news.photos.all()[:3]

    if request.method == 'POST':
        try:
            # Получаем данные из формы
            title = request.POST.get('title', '').strip()
            short_description = request.POST.get('short_description', '').strip()
            detailed_description = request.POST.get('detailed_description', '').strip()
            publish_date = request.POST.get('publish_date', '')
            status_id = request.POST.get('status', '')
            content_type_id = request.POST.get('content_type', '')
            target_audience_id = request.POST.get('target_audience', '')

            # Валидация
            if not title:
                messages.error(request, 'Заголовок новости обязателен')
                return render(request, 'admin_panel/news/form.html', {
                    'news': news,
                    'target_audiences': target_audiences,
                    'content_types': content_types,
                    'info_statuses': info_statuses,
                    'existing_photos': existing_photos,
                })

            # Обновляем новость
            news.title = title
            news.short_description = short_description
            news.detailed_description = detailed_description
            if publish_date:
                from datetime import datetime
                news.publication_date = datetime.strptime(publish_date, '%Y-%m-%d').date()
            news.target_audience_id = target_audience_id if target_audience_id else None
            news.content_type_id = content_type_id if content_type_id else None
            news.info_status_id = status_id
            news.is_published = True
            news.save()

            # Обработка удаления старых фото
            photos_to_delete = request.POST.getlist('delete_photos')
            for photo_id in photos_to_delete:
                try:
                    photo = NewsPhoto.objects.get(id=photo_id, news=news)
                    if photo.photo:
                        if os.path.isfile(photo.photo.path):
                            os.remove(photo.photo.path)
                    photo.delete()
                except NewsPhoto.DoesNotExist:
                    pass

            # Обработка новых фото
            new_photos = request.FILES.getlist('photos')
            current_photos_count = news.photos.count()

            for photo_file in new_photos:
                if current_photos_count < 3:
                    NewsPhoto.objects.create(
                        news=news,
                        photo=photo_file
                    )
                    current_photos_count += 1
                else:
                    messages.warning(request, 'Максимум 3 фото. Лишние фото не сохранены.')
                    break

            messages.success(request, 'Новость успешно обновлена')
            return redirect('admin_panel:news_list')

        except Exception as e:
            messages.error(request, f'Ошибка при обновлении новости: {str(e)}')

    # Подготавливаем данные для шаблона
    news_data = {
        'id': news.id,
        'title': news.title,
        'short_description': news.short_description,
        'detailed_description': news.detailed_description,
        'publish_date': news.publication_date.strftime('%Y-%m-%d'),
        'status_id': news.info_status_id,
        'content_type_id': news.content_type_id,
        'target_audience_id': news.target_audience_id,
        'created_at': news.created_at.strftime('%d.%m.%Y %H:%M') if news.created_at else '',
        'updated_at': news.updated_at.strftime('%d.%m.%Y %H:%M') if news.updated_at else '',
    }

    # Подготавливаем данные о существующих фото
    photos_data = []
    for photo in existing_photos:
        if photo.photo:
            photos_data.append({
                'id': photo.id,
                'url': photo.photo.url,
                'filename': os.path.basename(photo.photo.name),
            })

    return render(request, 'admin_panel/news/form.html', {
        'news': news_data,
        'target_audiences': target_audiences,
        'content_types': content_types,
        'info_statuses': info_statuses,
        'existing_photos': photos_data,
        'page_title': f'Редактирование: {news.title}',
        'admin_name': request.session.get('admin_name', 'Администратор'),
    })


@csrf_exempt
def news_delete(request, news_id):
    """Удаление новости из реальной БД"""
    if not check_admin_access(request):
        return redirect('admin_panel:admin_login')

    if request.method == 'POST':
        news = get_object_or_404(RealNews, id=news_id)

        # Удаляем связанные фото
        for photo in news.photos.all():
            if photo.photo:
                if os.path.isfile(photo.photo.path):
                    os.remove(photo.photo.path)
            photo.delete()

        news.delete()
        messages.success(request, 'Новость успешно удалена')

    return redirect('admin_panel:news_list')


# ========== МЕТОДИЧЕСКИЕ МАТЕРИАЛЫ ==========
def materials_list(request):
    """Список методических материалов из реальной БД"""
    if not check_admin_access(request):
        return redirect('admin_panel:admin_login')

    # Получаем фильтры из GET-параметров
    subject_filter = request.GET.get('subject')
    type_filter = request.GET.get('type')
    difficulty_filter = request.GET.get('difficulty')
    grade_filter = request.GET.get('grade')
    format_filter = request.GET.get('format')
    assessment_filter = request.GET.get('assessment')
    additional_filter = request.GET.get('additional')

    # Базовый запрос
    materials_queryset = RealMaterial.objects.all().select_related(
        'subject', 'material_type', 'difficulty', 'grade', 'format', 'assessment', 'additional'
    ).order_by('-created_at')

    # Применяем фильтры
    if subject_filter and subject_filter != '':
        materials_queryset = materials_queryset.filter(subject__name__icontains=subject_filter)

    if type_filter and type_filter != '':
        materials_queryset = materials_queryset.filter(material_type__name__icontains=type_filter)

    if difficulty_filter and difficulty_filter != '':
        materials_queryset = materials_queryset.filter(difficulty__name__icontains=difficulty_filter)

    if grade_filter and grade_filter != '':
        materials_queryset = materials_queryset.filter(grade__name__icontains=grade_filter)

    if format_filter and format_filter != '':
        materials_queryset = materials_queryset.filter(format__name__icontains=format_filter)

    if assessment_filter and assessment_filter != '':
        materials_queryset = materials_queryset.filter(assessment__name__icontains=assessment_filter)

    if additional_filter and additional_filter != '':
        materials_queryset = materials_queryset.filter(additional__name__icontains=additional_filter)

    # Пагинация - 8 элементов на страницу
    page = request.GET.get('page', 1)
    paginator = Paginator(materials_queryset, 8)

    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    # Получаем все справочники из БД для фильтров
    db_subjects = MaterialSubject.objects.all().order_by('name')
    db_types = MaterialType.objects.all().order_by('name')
    db_difficulty = DifficultyLevel.objects.all().order_by('name')
    db_grades = Grade.objects.all().order_by('name')
    db_formats = WorkFormat.objects.all().order_by('name')
    db_assessment = AssessmentSystem.objects.all().order_by('name')
    db_additional = AdditionalCategory.objects.all().order_by('name')

    # Подготавливаем данные для шаблона
    materials_data = []
    for material in page_obj:
        # Определяем иконку для файла по расширению
        file_extension = ''
        if material.file:
            file_extension = os.path.splitext(material.file.name)[1].lower()

        file_icon = 'fa-file-pdf'
        if file_extension in ['.doc', '.docx']:
            file_icon = 'fa-file-word'
        elif file_extension in ['.ppt', '.pptx']:
            file_icon = 'fa-file-powerpoint'
        elif file_extension in ['.xls', '.xlsx']:
            file_icon = 'fa-file-excel'
        elif file_extension in ['.txt']:
            file_icon = 'fa-file-alt'

        materials_data.append({
            'id': material.id,
            'title': material.title,
            'short_description': material.description,
            'subject': {
                'id': material.subject.id if material.subject else None,
                'name': material.subject.name if material.subject else 'Не указан',
                'value': material.subject.name.lower().replace(' ', '_') if material.subject else 'unknown',
                'bg_color': material.subject.bg_color if material.subject and hasattr(material.subject,
                                                                                      'bg_color') else 'rgba(184, 212, 232, 0.85)',
                'text_color': material.subject.text_color if material.subject and hasattr(material.subject,
                                                                                          'text_color') else '#0c4a6e',
            },
            'material_type': {
                'id': material.material_type.id if material.material_type else None,
                'name': material.material_type.name if material.material_type else 'Не указан',
                'value': material.material_type.name.lower().replace(' ', '_') if material.material_type else 'unknown',
                'bg_color': material.material_type.bg_color if material.material_type and hasattr(
                    material.material_type, 'bg_color') else 'rgba(201, 228, 202, 0.85)',
                'text_color': material.material_type.text_color if material.material_type and hasattr(
                    material.material_type, 'text_color') else '#1e5128',
            },
            'difficulty': {
                'id': material.difficulty.id if material.difficulty else None,
                'name': material.difficulty.name if material.difficulty else 'Не указан',
            },
            'grade': {
                'id': material.grade.id if material.grade else None,
                'name': material.grade.name if material.grade else 'Не указан',
            },
            'format': {
                'id': material.format.id if material.format else None,
                'name': material.format.name if material.format else 'Не указан',
            },
            'assessment': {
                'id': material.assessment.id if material.assessment else None,
                'name': material.assessment.name if material.assessment else 'Не указан',
            },
            'additional': {
                'id': material.additional.id if material.additional else None,
                'name': material.additional.name if material.additional else None,
            },
            'file_name': os.path.basename(material.file.name) if material.file else None,
            'file_size': material.file.size if material.file else 0,
            'file_icon': file_icon,
            'created_at': material.created_at.strftime('%d.%m.%Y') if material.created_at else '',
            'updated_at': material.updated_at.strftime('%d.%m.%Y') if material.updated_at else '',
            'downloads': 0,
            'views': 0,
            'rating': 0,
        })

    return render(request, 'admin_panel/materials/list.html', {
        'materials': materials_data,
        'page_obj': page_obj,
        'paginator': paginator,
        'subjects': MATERIAL_SUBJECTS,
        'types': MATERIAL_TYPES,
        'difficulty': MATERIAL_DIFFICULTY,
        'grades': MATERIAL_GRADES,
        'formats': MATERIAL_FORMATS,
        'assessment': MATERIAL_ASSESSMENT,
        'additional': MATERIAL_ADDITIONAL,
        'db_subjects': db_subjects,
        'db_types': db_types,
        'db_difficulty': db_difficulty,
        'db_grades': db_grades,
        'db_formats': db_formats,
        'db_assessment': db_assessment,
        'db_additional': db_additional,
        'current_filters': {
            'subject': subject_filter if subject_filter else '',
            'type': type_filter if type_filter else '',
            'difficulty': difficulty_filter if difficulty_filter else '',
            'grade': grade_filter if grade_filter else '',
            'format': format_filter if format_filter else '',
            'assessment': assessment_filter if assessment_filter else '',
            'additional': additional_filter if additional_filter else '',
        },
        'page_title': 'Методические материалы',
        'admin_name': request.session.get('admin_name', 'Администратор'),
    })


@csrf_exempt
def material_create(request):
    """Создание методического материала в реальной БД"""
    if not check_admin_access(request):
        return redirect('admin_panel:admin_login')

    # Получаем реальные справочники из БД
    subjects = MaterialSubject.objects.all().order_by('name')
    types = MaterialType.objects.all().order_by('name')
    difficulty = DifficultyLevel.objects.all().order_by('name')
    grades = Grade.objects.all().order_by('name')
    formats = WorkFormat.objects.all().order_by('name')
    assessment = AssessmentSystem.objects.all().order_by('name')
    additional = AdditionalCategory.objects.all().order_by('name')

    if request.method == 'POST':
        try:
            # Получаем данные из формы
            title = request.POST.get('title', '').strip()
            description = request.POST.get('short_description', '').strip()
            subject_id = request.POST.get('subject_area', '')
            material_type_id = request.POST.get('material_type', '')
            difficulty_id = request.POST.get('difficulty_level', '')
            grade_id = request.POST.get('grade', '')
            format_id = request.POST.get('work_format', '')
            assessment_id = request.POST.get('assessment_system', '')
            additional_id = request.POST.get('additional_category', '')

            # Валидация
            if not title:
                messages.error(request, 'Название материала обязательно')
                return render(request, 'admin_panel/materials/form.html', {
                    'subjects': subjects,
                    'types': types,
                    'difficulty': difficulty,
                    'grades': grades,
                    'formats': formats,
                    'assessment': assessment,
                    'additional': additional,
                })

            # Создаем материал
            material = RealMaterial.objects.create(
                title=title,
                description=description,
                subject_id=subject_id if subject_id else None,
                material_type_id=material_type_id if material_type_id else None,
                difficulty_id=difficulty_id if difficulty_id else None,
                grade_id=grade_id if grade_id else None,
                format_id=format_id if format_id else None,
                assessment_id=assessment_id if assessment_id else None,
                additional_id=additional_id if additional_id else None,
                is_published=True
            )

            # Обработка загруженного файла
            if 'file' in request.FILES:
                material.file = request.FILES['file']
                material.save()

            messages.success(request, 'Материал успешно создан')
            return redirect('admin_panel:materials_list')

        except Exception as e:
            messages.error(request, f'Ошибка при создании материала: {str(e)}')

    return render(request, 'admin_panel/materials/form.html', {
        'subjects': subjects,
        'types': types,
        'difficulty': difficulty,
        'grades': grades,
        'formats': formats,
        'assessment': assessment,
        'additional': additional,
        'page_title': 'Создание материала',
        'admin_name': request.session.get('admin_name', 'Администратор'),
    })


@csrf_exempt
def material_edit(request, material_id):
    """Редактирование методического материала в реальной БД"""
    if not check_admin_access(request):
        return redirect('admin_panel:admin_login')

    # Получаем материал из БД
    material = get_object_or_404(RealMaterial, id=material_id)

    # Получаем справочники
    subjects = MaterialSubject.objects.all().order_by('name')
    types = MaterialType.objects.all().order_by('name')
    difficulty = DifficultyLevel.objects.all().order_by('name')
    grades = Grade.objects.all().order_by('name')
    formats = WorkFormat.objects.all().order_by('name')
    assessment = AssessmentSystem.objects.all().order_by('name')
    additional = AdditionalCategory.objects.all().order_by('name')

    if request.method == 'POST':
        try:
            # Получаем данные из формы
            title = request.POST.get('title', '').strip()
            description = request.POST.get('short_description', '').strip()
            subject_id = request.POST.get('subject_area', '')
            material_type_id = request.POST.get('material_type', '')
            difficulty_id = request.POST.get('difficulty_level', '')
            grade_id = request.POST.get('grade', '')
            format_id = request.POST.get('work_format', '')
            assessment_id = request.POST.get('assessment_system', '')
            additional_id = request.POST.get('additional_category', '')

            # Валидация
            if not title:
                messages.error(request, 'Название материала обязательно')
                return render(request, 'admin_panel/materials/form.html', {
                    'material': material,
                    'subjects': subjects,
                    'types': types,
                    'difficulty': difficulty,
                    'grades': grades,
                    'formats': formats,
                    'assessment': assessment,
                    'additional': additional,
                })

            # Обновляем материал
            material.title = title
            material.description = description
            material.subject_id = subject_id if subject_id else None
            material.material_type_id = material_type_id if material_type_id else None
            material.difficulty_id = difficulty_id if difficulty_id else None
            material.grade_id = grade_id if grade_id else None
            material.format_id = format_id if format_id else None
            material.assessment_id = assessment_id if assessment_id else None
            material.additional_id = additional_id if additional_id else None

            # Обработка нового файла
            if 'file' in request.FILES:
                if material.file:
                    if os.path.isfile(material.file.path):
                        os.remove(material.file.path)
                material.file = request.FILES['file']

            material.save()

            messages.success(request, 'Материал успешно обновлен')
            return redirect('admin_panel:materials_list')

        except Exception as e:
            messages.error(request, f'Ошибка при обновлении материала: {str(e)}')

    # Подготавливаем данные для шаблона
    material_data = {
        'id': material.id,
        'title': material.title,
        'short_description': material.description,
        'subject_id': material.subject_id,
        'material_type_id': material.material_type_id,
        'difficulty_id': material.difficulty_id,
        'grade_id': material.grade_id,
        'format_id': material.format_id,
        'assessment_id': material.assessment_id,
        'additional_id': material.additional_id,
        'file_name': os.path.basename(material.file.name) if material.file else None,
        'file_size': material.file.size if material.file else 0,
        'created_at': material.created_at.strftime('%d.%m.%Y') if material.created_at else '',
        'updated_at': material.updated_at.strftime('%d.%m.%Y') if material.updated_at else '',
        'is_published': material.is_published,
    }

    return render(request, 'admin_panel/materials/form.html', {
        'material': material_data,
        'subjects': subjects,
        'types': types,
        'difficulty': difficulty,
        'grades': grades,
        'formats': formats,
        'assessment': assessment,
        'additional': additional,
        'page_title': f'Редактирование: {material.title}',
        'admin_name': request.session.get('admin_name', 'Администратор'),
    })


@csrf_exempt
def material_delete(request, material_id):
    """Удаление методического материала из реальной БД"""
    if not check_admin_access(request):
        return redirect('admin_panel:admin_login')

    if request.method == 'POST':
        material = get_object_or_404(RealMaterial, id=material_id)

        # Удаляем файл
        if material.file:
            if os.path.isfile(material.file.path):
                os.remove(material.file.path)

        material.delete()
        messages.success(request, 'Материал успешно удален')

    return redirect('admin_panel:materials_list')


# ========== НОРМАТИВНЫЕ ДОКУМЕНТЫ ==========
def documents_list(request):
    """Список нормативных документов из реальной БД"""
    if not check_admin_access(request):
        return redirect('admin_panel:admin_login')

    # Получаем фильтры из GET-параметров
    category_filter = request.GET.get('category')
    level_filter = request.GET.get('level')
    year_filter = request.GET.get('year')

    # Базовый запрос
    documents_queryset = RealDocument.objects.all().select_related(
        'category', 'level'
    ).order_by('-publication_date')

    # Применяем фильтры
    if category_filter and category_filter != '':
        documents_queryset = documents_queryset.filter(category__name__icontains=category_filter)

    if level_filter and level_filter != '':
        documents_queryset = documents_queryset.filter(level__name__icontains=level_filter)

    if year_filter and year_filter != '':
        documents_queryset = documents_queryset.filter(publication_date__year=year_filter)

    # Пагинация - 8 элементов на страницу
    page = request.GET.get('page', 1)
    paginator = Paginator(documents_queryset, 8)

    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    # Получаем все справочники из БД для фильтров
    db_categories = DocumentCategory.objects.all().order_by('name')
    db_levels = ActionLevel.objects.all().order_by('name')

    # Получаем уникальные годы для фильтра
    years_list = RealDocument.objects.filter(is_published=True).dates('publication_date', 'year')
    years_data = []
    for year_date in years_list:
        year_str = str(year_date.year)
        years_data.append({'id': year_str, 'name': year_str})
    years_data.append({'id': 'old', 'name': '2020 и ранее'})

    # Подготавливаем данные для шаблона
    documents_data = []
    for doc in page_obj:
        # Определяем иконку для файла по расширению
        file_extension = ''
        if doc.file:
            file_extension = os.path.splitext(doc.file.name)[1].lower()

        file_type = 'PDF'
        if file_extension in ['.doc', '.docx']:
            file_type = 'Word'
        elif file_extension in ['.xls', '.xlsx']:
            file_type = 'Excel'
        elif file_extension in ['.rtf']:
            file_type = 'RTF'
        elif file_extension in ['.txt']:
            file_type = 'TXT'

        documents_data.append({
            'id': doc.id,
            'title': doc.title,
            'short_description': doc.description,
            'publication_date': doc.publication_date.strftime('%Y-%m-%d'),
            'publication_date_display': doc.publication_date.strftime('%d.%m.%Y'),
            'file_size': doc.file_size,
            'file_size_display': doc.file_size_display,
            'file_name': os.path.basename(doc.file.name) if doc.file else None,
            'file_type': file_type,
            'category': {
                'id': doc.category.id if doc.category else None,
                'name': doc.category.name if doc.category else 'Не указан',
                'bg_color': doc.category.bg_color if doc.category and hasattr(doc.category,
                                                                              'bg_color') else 'rgba(184, 212, 232, 0.85)',
                'text_color': doc.category.text_color if doc.category and hasattr(doc.category,
                                                                                  'text_color') else '#0c4a6e',
            },
            'level': {
                'id': doc.level.id if doc.level else None,
                'name': doc.level.name if doc.level else 'Не указан',
                'value': doc.level.name.lower() if doc.level else 'unknown',
            },
            'year': doc.publication_date.year,
            'created_at': doc.created_at.strftime('%d.%m.%Y') if doc.created_at else '',
            'updated_at': doc.updated_at.strftime('%d.%m.%Y') if doc.updated_at else '',
        })

    return render(request, 'admin_panel/documents/list.html', {
        'documents': documents_data,
        'page_obj': page_obj,
        'paginator': paginator,
        'categories': DOCUMENT_CATEGORIES,
        'levels': DOCUMENT_LEVELS,
        'years': years_data,
        'db_categories': db_categories,
        'db_levels': db_levels,
        'current_filters': {
            'category': category_filter if category_filter else '',
            'level': level_filter if level_filter else '',
            'year': year_filter if year_filter else '',
        },
        'page_title': 'Нормативные документы',
        'admin_name': request.session.get('admin_name', 'Администратор'),
    })


@csrf_exempt
def documents_create(request):
    """Создание нормативного документа в реальной БД"""
    if not check_admin_access(request):
        return redirect('admin_panel:admin_login')

    # Получаем реальные справочники из БД
    categories = DocumentCategory.objects.all().order_by('name')
    levels = ActionLevel.objects.all().order_by('name')

    if request.method == 'POST':
        try:
            # Получаем данные из формы
            title = request.POST.get('title', '').strip()
            description = request.POST.get('short_description', '').strip()  # В форме это short_description
            full_description = request.POST.get('full_description', '').strip()  # Это поле может быть в форме
            publication_date = request.POST.get('publish_date', '')
            category_id = request.POST.get('category', '')
            level_id = request.POST.get('action_level', '')
            file_size = request.POST.get('file_size', '0')

            # Валидация
            if not title:
                messages.error(request, 'Название документа обязательно')
                return render(request, 'admin_panel/documents/form.html', {
                    'categories': categories,
                    'levels': levels,
                })

            if not category_id:
                messages.error(request, 'Категория документа обязательна')
                return render(request, 'admin_panel/documents/form.html', {
                    'categories': categories,
                    'levels': levels,
                })

            if not level_id:
                messages.error(request, 'Уровень действия обязателен')
                return render(request, 'admin_panel/documents/form.html', {
                    'categories': categories,
                    'levels': levels,
                })

            # Парсим дату
            from datetime import datetime
            pub_date = datetime.strptime(publication_date, '%Y-%m-%d').date() if publication_date else None

            # ИСПРАВЛЕНО: Используем правильные названия полей
            document = RealDocument.objects.create(
                title=title,
                description=description,  # В модели поле называется description
                # Если в модели есть поле full_description, раскомментируйте:
                # full_description=full_description,
                publication_date=pub_date,
                category_id=category_id,
                level_id=level_id,
                file_size=int(file_size) if file_size else 0,
                is_published=True
            )

            # Обработка загруженного файла
            if 'file' in request.FILES:
                document.file = request.FILES['file']
                document.save()

            messages.success(request, 'Документ успешно создан')
            return redirect('admin_panel:documents_list')

        except Exception as e:
            messages.error(request, f'Ошибка при создании документа: {str(e)}')

    return render(request, 'admin_panel/documents/form.html', {
        'categories': categories,
        'levels': levels,
        'page_title': 'Создание документа',
        'admin_name': request.session.get('admin_name', 'Администратор'),
    })


@csrf_exempt
def documents_edit(request, document_id):
    """Редактирование нормативного документа в реальной БД"""
    if not check_admin_access(request):
        return redirect('admin_panel:admin_login')

    # Получаем документ из БД
    document = get_object_or_404(RealDocument, id=document_id)

    # Получаем справочники
    categories = DocumentCategory.objects.all().order_by('name')
    levels = ActionLevel.objects.all().order_by('name')

    if request.method == 'POST':
        try:
            # Получаем данные из формы
            title = request.POST.get('title', '').strip()
            description = request.POST.get('short_description', '').strip()
            full_description = request.POST.get('full_description', '').strip()  # Это поле может быть в форме
            publication_date = request.POST.get('publish_date', '')
            category_id = request.POST.get('category', '')
            level_id = request.POST.get('action_level', '')
            file_size = request.POST.get('file_size', '0')

            # Валидация
            if not title:
                messages.error(request, 'Название документа обязательно')
                return render(request, 'admin_panel/documents/form.html', {
                    'document': document,
                    'categories': categories,
                    'levels': levels,
                })

            # Парсим дату
            from datetime import datetime
            pub_date = datetime.strptime(publication_date, '%Y-%m-%d').date() if publication_date else None

            # ИСПРАВЛЕНО: Используем правильные названия полей
            document.title = title
            document.description = description  # В модели поле называется description
            # Если в модели есть поле full_description, раскомментируйте:
            # document.full_description = full_description
            document.publication_date = pub_date
            document.category_id = category_id if category_id else None
            document.level_id = level_id if level_id else None
            document.file_size = int(file_size) if file_size else 0

            # Обработка нового файла
            if 'file' in request.FILES:
                if document.file:
                    if os.path.isfile(document.file.path):
                        os.remove(document.file.path)
                document.file = request.FILES['file']

            document.save()

            messages.success(request, 'Документ успешно обновлен')
            return redirect('admin_panel:documents_list')

        except Exception as e:
            messages.error(request, f'Ошибка при обновлении документа: {str(e)}')

    # ИСПРАВЛЕНО: Подготавливаем данные для шаблона с правильными названиями полей
    document_data = {
        'id': document.id,
        'title': document.title,
        'short_description': document.description,  # В модели поле называется description
        # Если в модели есть поле full_description, используйте его:
        # 'full_description': document.full_description if hasattr(document, 'full_description') else '',
        'publication_date': document.publication_date.strftime('%Y-%m-%d') if document.publication_date else '',
        'category_id': document.category_id,
        'level_id': document.level_id,
        'file_size': document.file_size,
        'file_name': os.path.basename(document.file.name) if document.file else None,
        'created_at': document.created_at.strftime('%d.%m.%Y') if document.created_at else '',
        'updated_at': document.updated_at.strftime('%d.%m.%Y') if document.updated_at else '',
        'is_published': document.is_published,
    }

    return render(request, 'admin_panel/documents/form.html', {
        'document': document_data,
        'categories': categories,
        'levels': levels,
        'page_title': f'Редактирование: {document.title}',
        'admin_name': request.session.get('admin_name', 'Администратор'),
    })


@csrf_exempt
def documents_delete(request, document_id):
    """Удаление нормативного документа из реальной БД"""
    if not check_admin_access(request):
        return redirect('admin_panel:admin_login')

    if request.method == 'POST':
        document = get_object_or_404(RealDocument, id=document_id)

        # Удаляем файл
        if document.file:
            if os.path.isfile(document.file.path):
                os.remove(document.file.path)

        document.delete()
        messages.success(request, 'Документ успешно удален')

    return redirect('admin_panel:documents_list')


# ========== ОПРОСЫ ==========


def surveys_list(request):
    """Список опросов с фильтрацией и пагинацией"""
    if not check_admin_access(request):
        return redirect('admin_panel:admin_login')

    # Получаем параметры фильтрации из GET-запроса
    category_filter = request.GET.get('category')
    status_filter = request.GET.get('status')      # 'active' или 'completed'
    duration_filter = request.GET.get('duration')

    # Базовый запрос (все опросы, подгружаем связанные данные)
    surveys_queryset = Survey.objects.all().select_related(
        'category', 'status'
    ).prefetch_related('questions').order_by('-created_date')

    # Фильтр по категории (поиск по имени категории, без учёта регистра)
    if category_filter and category_filter.strip():
        surveys_queryset = surveys_queryset.filter(category__name__icontains=category_filter)

    # ========== ИСПРАВЛЕННЫЙ ФИЛЬТР ПО СТАТУСУ ==========
    # Вместо сравнения строк ищем ID статуса по части имени
    if status_filter and status_filter.strip():
        if status_filter == 'active':
            try:
                active_status = ActivityStatus.objects.get(name__icontains='актив')
                surveys_queryset = surveys_queryset.filter(status_id=active_status.id)
            except ActivityStatus.DoesNotExist:
                messages.warning(request, 'Статус "Активный" не найден в справочнике')
        elif status_filter == 'completed':
            try:
                completed_status = ActivityStatus.objects.get(name__icontains='заверш')
                surveys_queryset = surveys_queryset.filter(status_id=completed_status.id)
            except ActivityStatus.DoesNotExist:
                messages.warning(request, 'Статус "Завершённый" не найден в справочнике')
        # Если пришло что-то другое – игнорируем

    # Фильтр по длительности
    if duration_filter and duration_filter.strip():
        if duration_filter == 'short':
            surveys_queryset = surveys_queryset.filter(duration__in=['До 10 мин', '5-10 мин', '5-10 минут'])
        elif duration_filter == 'medium':
            surveys_queryset = surveys_queryset.filter(duration__in=['10-15 мин', '10-15 минут', '15 мин'])
        elif duration_filter == 'long':
            surveys_queryset = surveys_queryset.filter(duration__in=['Более 15 мин', '20-30 мин', '30 мин'])

    # Пагинация (8 опросов на страницу)
    paginator = Paginator(surveys_queryset, 8)
    page = request.GET.get('page', 1)
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    # Получаем справочники для выпадающих списков фильтров
    db_categories = SurveyCategory.objects.all().order_by('name')
    db_statuses = ActivityStatus.objects.all().order_by('name')

    # ========== ОПРЕДЕЛЕНИЕ ID СТАТУСОВ ДЛЯ ОТОБРАЖЕНИЯ ==========
    # Получаем ID активного и завершённого статусов (один раз)
    active_status_id = None
    completed_status_id = None
    try:
        active_status = ActivityStatus.objects.get(name__icontains='актив')
        active_status_id = active_status.id
    except ActivityStatus.DoesNotExist:
        pass
    try:
        completed_status = ActivityStatus.objects.get(name__icontains='заверш')
        completed_status_id = completed_status.id
    except ActivityStatus.DoesNotExist:
        pass

    # Формируем список опросов для шаблона
    surveys_data = []
    for survey in page_obj:
        questions_count = survey.questions.count()
        responses_count = SurveyPassing.objects.filter(survey=survey).count()

        # Определяем класс статуса и отображаемое название
        if active_status_id is not None and survey.status_id == active_status_id:
            status_class = 'active'
            status_display = 'Активный'
        elif completed_status_id is not None and survey.status_id == completed_status_id:
            status_class = 'completed'
            status_display = 'Завершённый'
        else:
            # Если статус не распознан – считаем завершённым и выводим название из БД
            status_class = 'completed'
            status_display = survey.status.name if survey.status else 'Неизвестно'

        surveys_data.append({
            'id': survey.id,
            'title': survey.title,
            'short_description': survey.description,
            'category_name': survey.category.name if survey.category else 'Без категории',
            'status': status_class,
            'status_display': status_display,
            'responses': responses_count,
            'questions_count': questions_count,
            'duration_display': survey.duration,
        })

    context = {
        'surveys': surveys_data,
        'page_obj': page_obj,
        'paginator': paginator,
        'categories': db_categories,
        'statuses': SURVEY_STATUSES,          # если у вас есть такая константа
        'db_categories': db_categories,
        'db_statuses': db_statuses,
        'current_filters': {
            'category': category_filter or '',
            'status': status_filter or '',
            'duration': duration_filter or '',
        },
        'page_title': 'Опросы',
        'admin_name': request.session.get('admin_name', 'Администратор'),
    }

    return render(request, 'admin_panel/surveys/list.html', context)


def change_survey_status(request, survey_id, new_status):
    """
    Изменение статуса опроса.
    new_status может быть 'active' или 'completed'.
    """
    if not check_admin_access(request):
        return redirect('admin_panel:admin_login')

    survey = get_object_or_404(Survey, id=survey_id)

    if new_status == 'active':
        try:
            # Ищем статус, содержащий подстроку "актив" (без учёта регистра)
            status_obj = ActivityStatus.objects.get(name__icontains='актив')
            survey.status = status_obj
            survey.save()
            messages.success(request, f'Опрос "{survey.title}" активирован.')
        except ActivityStatus.DoesNotExist:
            messages.error(request, 'Не удалось активировать опрос: статус "Активный" не найден в справочнике.')
    elif new_status == 'completed':
        try:
            status_obj = ActivityStatus.objects.get(name__icontains='заверш')
            survey.status = status_obj
            survey.save()
            messages.success(request, f'Опрос "{survey.title}" завершён.')
        except ActivityStatus.DoesNotExist:
            messages.error(request, 'Не удалось завершить опрос: статус "Завершённый" не найден в справочнике.')
    else:
        messages.error(request, f'Некорректное значение статуса: {new_status}. Допустимые значения: active, completed.')

    return redirect('admin_panel:surveys_list')

@csrf_exempt
def survey_create(request):
    """Создание опроса в реальной БД"""
    if not check_admin_access(request):
        return redirect('admin_panel:admin_login')

    # Получаем реальные справочники из БД
    categories = SurveyCategory.objects.all().order_by('name')
    statuses = ActivityStatus.objects.all().order_by('name')

    if request.method == 'POST':
        try:
            # Получаем данные из формы
            title = request.POST.get('title', '').strip()
            description = request.POST.get('short_description', '').strip()
            category_id = request.POST.get('category', '')
            duration = request.POST.get('duration', '10-15 мин')
            status_id = request.POST.get('status', '')

            # Валидация
            if not title:
                messages.error(request, 'Название опроса обязательно')
                return render(request, 'admin_panel/surveys/form.html', {
                    'categories': categories,
                    'statuses': statuses,
                })

            if not category_id:
                messages.error(request, 'Категория обязательна')
                return render(request, 'admin_panel/surveys/form.html', {
                    'categories': categories,
                    'statuses': statuses,
                })

            if not status_id:
                messages.error(request, 'Статус обязателен')
                return render(request, 'admin_panel/surveys/form.html', {
                    'categories': categories,
                    'statuses': statuses,
                })

            # Создаем опрос
            survey = RealSurvey.objects.create(
                title=title,
                description=description,
                category_id=category_id,
                duration=duration,
                status_id=status_id,
                questions_count=0
            )

            messages.success(request, 'Опрос успешно создан')
            return redirect('admin_panel:survey_edit', survey_id=survey.id)

        except Exception as e:
            messages.error(request, f'Ошибка при создании опроса: {str(e)}')

    return render(request, 'admin_panel/surveys/form.html', {
        'categories': categories,
        'statuses': statuses,
        'page_title': 'Создание опроса',
        'admin_name': request.session.get('admin_name', 'Администратор'),
    })


@csrf_exempt
def survey_edit(request, survey_id):
    """Редактирование опроса в реальной БД"""
    if not check_admin_access(request):
        return redirect('admin_panel:admin_login')

    # Получаем опрос из БД
    survey = get_object_or_404(RealSurvey, id=survey_id)

    # Получаем справочники
    categories = SurveyCategory.objects.all().order_by('name')
    statuses = ActivityStatus.objects.all().order_by('name')
    question_types = QuestionType.objects.all().order_by('name')

    # Получаем вопросы для этого опроса
    questions = survey.questions.all().order_by('order')
    questions_data = []

    for question in questions:
        options = question.options.all().order_by('order')
        options_data = [{'id': opt.id, 'text': opt.text} for opt in options]

        questions_data.append({
            'id': question.id,
            'text': question.text,
            'question_type': question.question_type.id if question.question_type else None,
            'order': question.order,
            'is_required': question.is_required,
            'options': options_data,
        })

    if request.method == 'POST':
        # Сохраняем изменения опроса
        if 'save_survey' in request.POST:
            try:
                title = request.POST.get('title', '').strip()
                description = request.POST.get('short_description', '').strip()
                category_id = request.POST.get('category', '')
                duration = request.POST.get('duration', '')
                status_id = request.POST.get('status', '')

                if not title:
                    messages.error(request, 'Название опроса обязательно')
                else:
                    survey.title = title
                    survey.description = description
                    survey.category_id = category_id
                    survey.duration = duration if duration else '10-15 мин'
                    survey.status_id = status_id
                    survey.save()

                    messages.success(request, 'Опрос обновлен')

            except Exception as e:
                messages.error(request, f'Ошибка при обновлении опроса: {str(e)}')

        return redirect('admin_panel:survey_edit', survey_id=survey_id)

    # Подготавливаем данные для шаблона
    survey_data = {
        'id': survey.id,
        'title': survey.title,
        'short_description': survey.description,
        'category_id': survey.category_id,
        'duration': survey.duration,
        'status_id': survey.status_id,
        'created_at': survey.created_date.strftime('%d.%m.%Y') if survey.created_date else '',
        'updated_at': survey.updated_at.strftime('%d.%m.%Y') if survey.updated_at else '',
        'questions_count': survey.questions_count,
    }

    return render(request, 'admin_panel/surveys/edit.html', {
        'survey': survey_data,
        'questions': questions_data,
        'categories': categories,
        'statuses': statuses,
        'question_types': question_types,
        'page_title': f'Редактирование: {survey.title}',
        'admin_name': request.session.get('admin_name', 'Администратор'),
    })


@csrf_exempt
def survey_delete(request, survey_id):
    """Удаление опроса из реальной БД"""
    if not check_admin_access(request):
        return redirect('admin_panel:admin_login')

    if request.method == 'POST':
        survey = get_object_or_404(RealSurvey, id=survey_id)

        # Удаляем связанные вопросы и ответы (каскадно)
        survey.delete()
        messages.success(request, 'Опрос и все связанные вопросы удалены')

    return redirect('admin_panel:surveys_list')


# ========== ВОПРОСЫ ==========
@csrf_exempt
def question_create(request, survey_id):
    """Создание нового вопроса для опроса"""
    if not check_admin_access(request):
        return redirect('admin_panel:admin_login')

    survey = get_object_or_404(RealSurvey, id=survey_id)
    question_types = QuestionType.objects.all().order_by('name')

    if request.method == 'POST':
        try:
            question_text = request.POST.get('question_text', '').strip()
            question_type_id = request.POST.get('question_type', '')
            is_required = request.POST.get('is_required') == 'on'

            if not question_text:
                messages.error(request, 'Текст вопроса обязателен')
            elif not question_type_id:
                messages.error(request, 'Тип вопроса обязателен')
            else:
                # Создаем вопрос
                question = Question.objects.create(
                    survey=survey,
                    text=question_text,
                    question_type_id=question_type_id,
                    order=survey.questions.count() + 1,
                    is_required=is_required
                )

                # Добавляем варианты ответов для вопросов с выбором
                question_type = QuestionType.objects.get(id=question_type_id)
                if question_type.name in ['Одиночный выбор', 'Множественный выбор']:
                    option_texts = request.POST.getlist('option_text[]')
                    for i, text in enumerate(option_texts):
                        if text.strip():
                            AnswerOption.objects.create(
                                question=question,
                                text=text.strip(),
                                order=i + 1
                            )

                # Обновляем счетчик вопросов
                survey.questions_count = survey.questions.count()
                survey.save()

                messages.success(request, 'Вопрос успешно добавлен')
                return redirect('admin_panel:survey_edit', survey_id=survey_id)

        except Exception as e:
            messages.error(request, f'Ошибка при создании вопроса: {str(e)}')

    return render(request, 'admin_panel/surveys/question_create.html', {
        'survey': survey,
        'question_types': question_types,
        'page_title': f'Добавление вопроса к опросу: {survey.title}',
        'admin_name': request.session.get('admin_name', 'Администратор'),
    })


@csrf_exempt
def question_edit(request, survey_id, question_id):
    """Редактирование вопроса в реальной БД"""
    if not check_admin_access(request):
        return redirect('admin_panel:admin_login')

    survey = get_object_or_404(RealSurvey, id=survey_id)
    question = get_object_or_404(Question, id=question_id, survey=survey)

    # Получаем варианты ответов
    options = question.options.all().order_by('order')
    options_data = [{'id': opt.id, 'text': opt.text} for opt in options]

    question_types = QuestionType.objects.all().order_by('name')

    if request.method == 'POST':
        try:
            question_text = request.POST.get('question_text', '').strip()
            question_type_id = request.POST.get('question_type', '')
            is_required = request.POST.get('is_required') == 'on'

            if not question_text:
                messages.error(request, 'Текст вопроса обязателен')
            else:
                # Обновляем вопрос
                question.text = question_text
                question.question_type_id = question_type_id
                question.is_required = is_required
                question.save()

                # Обновляем варианты ответов
                option_texts = request.POST.getlist('option_text[]')
                option_ids = request.POST.getlist('option_id[]')

                # Удаляем старые варианты
                question.options.all().delete()

                # Добавляем новые варианты
                for i, text in enumerate(option_texts):
                    if text.strip():
                        AnswerOption.objects.create(
                            question=question,
                            text=text.strip(),
                            order=i + 1
                        )

                messages.success(request, 'Вопрос обновлен')
                return redirect('admin_panel:survey_edit', survey_id=survey_id)

        except Exception as e:
            messages.error(request, f'Ошибка при обновлении вопроса: {str(e)}')

    # Подготавливаем данные для шаблона
    question_data = {
        'id': question.id,
        'text': question.text,
        'question_type': question.question_type.id if question.question_type else None,
        'is_required': question.is_required,
        'options': options_data,
    }

    return render(request, 'admin_panel/surveys/question_edit.html', {
        'question': question_data,
        'survey': survey,
        'question_types': question_types,
        'page_title': 'Редактирование вопроса',
        'admin_name': request.session.get('admin_name', 'Администратор'),
    })


@csrf_exempt
def question_delete(request, survey_id, question_id):
    """Удаление вопроса из реальной БД"""
    if not check_admin_access(request):
        return redirect('admin_panel:admin_login')

    if request.method == 'POST':
        question = get_object_or_404(Question, id=question_id)
        question.delete()

        # Обновляем порядок вопросов
        survey = get_object_or_404(RealSurvey, id=survey_id)
        for i, q in enumerate(survey.questions.all().order_by('id')):
            q.order = i + 1
            q.save()

        survey.questions_count = survey.questions.count()
        survey.save()

        messages.success(request, 'Вопрос удален')

    return redirect('admin_panel:survey_edit', survey_id=survey_id)





# ========== ДЕМО ДАННЫЕ ==========
def create_demo_data(request):
    """Создание демо данных (для обратной совместимости)"""
    if not check_admin_access(request):
        return redirect('admin_panel:admin_login')

    messages.success(request, 'Демо данные уже существуют в БД')
    return redirect('admin_panel:dashboard')


@csrf_exempt
def check_admin_code(request):
    """
    Проверка секретного кода для двухфакторной аутентификации
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            entered_code = data.get('code', '').strip()

            if entered_code == settings.ADMIN_SECRET_CODE or entered_code == settings.ADMIN_BACKUP_CODE:
                request.session['admin_code_verified'] = True
                request.session.set_expiry(1800)

                return JsonResponse({
                    'success': True,
                    'redirect_url': reverse('admin_panel:admin_login')
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Неверный код доступа'
                })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Ошибка при обработке запроса: {str(e)}'
            })

    return JsonResponse({'success': False, 'error': 'Метод не поддерживается'})


def help(request):
    if not check_admin_access(request):
        return redirect('admin_panel:admin_login')

    context = {
        'page_title': 'Помощь и поддержка',
        'admin_name': request.session.get('admin_name', 'Администратор'),
        'admin_email': request.session.get('admin_email', ''),
    }
    return render(request, 'admin_panel/help.html', context)


from django.contrib.auth import update_session_auth_hash
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json


@csrf_exempt
@require_POST
def change_admin_password(request):
    """Смена пароля администратора (AJAX)"""
    if not check_admin_access(request):
        return JsonResponse({'success': False, 'error': 'Доступ запрещён'}, status=403)

    try:
        data = json.loads(request.body)
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')

        if new_password != confirm_password:
            return JsonResponse({'success': False, 'error': 'Пароли не совпадают'})

        if len(new_password) < 8:
            return JsonResponse({'success': False, 'error': 'Пароль должен содержать минимум 8 символов'})

        admin_id = request.session.get('admin_id')
        if not admin_id:
            return JsonResponse({'success': False, 'error': 'Сессия не найдена. Войдите заново.'})

        from admin_panel.models import AdminUser
        try:
            admin_user = AdminUser.objects.get(id=admin_id, is_active=True)
        except AdminUser.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Администратор не найден'})

        # Проверка старого пароля
        if not admin_user.check_password(old_password):
            return JsonResponse({'success': False, 'error': 'Неверный текущий пароль'})

        # Смена пароля
        admin_user.set_password(new_password)
        admin_user.save()

        return JsonResponse({'success': True, 'message': 'Пароль успешно изменён'})

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Неверный формат запроса'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})



from success_practices.models import Practice, PracticeCategory
from django.utils import timezone


def practices_list(request):
    """Список успешных практик"""
    if not check_admin_access(request):
        return redirect('admin_panel:admin_login')

    # Получаем фильтры
    category_filter = request.GET.get('category')
    audience_filter = request.GET.get('audience')
    format_filter = request.GET.get('format')
    difficulty_filter = request.GET.get('difficulty')

    practices_queryset = Practice.objects.all().select_related('category')

    if category_filter and category_filter != '':
        practices_queryset = practices_queryset.filter(category_id=category_filter)
    if audience_filter and audience_filter != '':
        practices_queryset = practices_queryset.filter(audience=audience_filter)
    if format_filter and format_filter != '':
        practices_queryset = practices_queryset.filter(format_type=format_filter)
    if difficulty_filter and difficulty_filter != '':
        practices_queryset = practices_queryset.filter(difficulty=difficulty_filter)

    practices_queryset = practices_queryset.order_by('-created_date')

    page = request.GET.get('page', 1)
    paginator = Paginator(practices_queryset, 10)

    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    categories = PracticeCategory.objects.all().order_by('name')

    practices_data = []
    for practice in page_obj:
        practices_data.append({
            'id': practice.id,
            'title': practice.title,
            'short_description': practice.short_description,
            'category_name': practice.category.name,
            'category_icon': practice.category.icon,
            'category_icon_color': practice.category.icon_color,
            'audience_display': practice.audience_display,
            'format_display': practice.format_display,
            'difficulty_display': practice.difficulty_display,
            'difficulty_icon': practice.difficulty_icon,
            'difficulty_color': practice.difficulty_color,
            'status_display': 'Опубликовано' if practice.is_published else 'Черновик',
            'created_date': practice.created_date.strftime('%d.%m.%Y'),
        })

    context = {
        'practices': practices_data,
        'page_obj': page_obj,
        'paginator': paginator,
        'categories': categories,
        'current_filters': {
            'category': category_filter or '',
            'audience': audience_filter or '',
            'format': format_filter or '',
            'difficulty': difficulty_filter or '',
        },
        'page_title': 'Успешные практики',
        'admin_name': request.session.get('admin_name', 'Администратор'),
    }

    return render(request, 'admin_panel/practices/list.html', context)


@csrf_exempt
def practice_create(request):
    """Создание практики"""
    if not check_admin_access(request):
        return redirect('admin_panel:admin_login')

    categories = PracticeCategory.objects.all().order_by('name')

    if request.method == 'POST':
        try:
            title = request.POST.get('title', '').strip()
            short_description = request.POST.get('short_description', '').strip()
            full_description = request.POST.get('full_description', '').strip()
            category_id = request.POST.get('category', '')
            audience = request.POST.get('audience', '')
            format_type = request.POST.get('format_type', '')
            difficulty = request.POST.get('difficulty', '')

            if not title:
                messages.error(request, 'Название практики обязательно')
                return render(request, 'admin_panel/practices/form.html', {'categories': categories})

            if not short_description:
                messages.error(request, 'Краткое описание обязательно')
                return render(request, 'admin_panel/practices/form.html', {'categories': categories})

            if not category_id:
                messages.error(request, 'Категория обязательна')
                return render(request, 'admin_panel/practices/form.html', {'categories': categories})

            # is_published всегда True, дата создаётся автоматически
            practice = Practice.objects.create(
                title=title,
                short_description=short_description,
                full_description=full_description,
                category_id=category_id,
                audience=audience if audience else None,
                format_type=format_type if format_type else None,
                difficulty=difficulty if difficulty else None,
                is_published=True
            )

            if 'file' in request.FILES:
                practice.file = request.FILES['file']
                practice.save()

            messages.success(request, f'Практика "{title}" успешно создана')
            return redirect('admin_panel:practices_list')

        except Exception as e:
            messages.error(request, f'Ошибка при создании практики: {str(e)}')

    return render(request, 'admin_panel/practices/form.html', {
        'categories': categories,
        'page_title': 'Создание практики',
        'admin_name': request.session.get('admin_name', 'Администратор'),
    })


@csrf_exempt
def practice_edit(request, practice_id):
    """Редактирование практики"""
    if not check_admin_access(request):
        return redirect('admin_panel:admin_login')

    practice = get_object_or_404(Practice, id=practice_id)
    categories = PracticeCategory.objects.all().order_by('name')

    if request.method == 'POST':
        try:
            title = request.POST.get('title', '').strip()
            short_description = request.POST.get('short_description', '').strip()
            full_description = request.POST.get('full_description', '').strip()
            category_id = request.POST.get('category', '')
            audience = request.POST.get('audience', '')
            format_type = request.POST.get('format_type', '')
            difficulty = request.POST.get('difficulty', '')
            remove_file = request.POST.get('remove_file') == 'true'

            if not title:
                messages.error(request, 'Название практики обязательно')
                return render(request, 'admin_panel/practices/form.html', {'practice': practice, 'categories': categories})

            if not short_description:
                messages.error(request, 'Краткое описание обязательно')
                return render(request, 'admin_panel/practices/form.html', {'practice': practice, 'categories': categories})

            if not category_id:
                messages.error(request, 'Категория обязательна')
                return render(request, 'admin_panel/practices/form.html', {'practice': practice, 'categories': categories})

            practice.title = title
            practice.short_description = short_description
            practice.full_description = full_description
            practice.category_id = category_id
            practice.audience = audience if audience else None
            practice.format_type = format_type if format_type else None
            practice.difficulty = difficulty if difficulty else None
            practice.is_published = True  # всегда опубликовано

            if remove_file and practice.file:
                if os.path.isfile(practice.file.path):
                    os.remove(practice.file.path)
                practice.file = None

            if 'file' in request.FILES:
                if practice.file and os.path.isfile(practice.file.path):
                    os.remove(practice.file.path)
                practice.file = request.FILES['file']

            practice.save()

            messages.success(request, f'Практика "{title}" успешно обновлена')
            return redirect('admin_panel:practices_list')

        except Exception as e:
            messages.error(request, f'Ошибка при обновлении практики: {str(e)}')

    practice_data = {
        'id': practice.id,
        'title': practice.title,
        'short_description': practice.short_description,
        'full_description': practice.full_description,
        'category_id': practice.category_id,
        'audience': practice.audience,
        'format_type': practice.format_type,
        'difficulty': practice.difficulty,
        'file_name': os.path.basename(practice.file.name) if practice.file else None,
        'file_size': practice.file.size if practice.file else 0,
        'created_at': practice.created_at.strftime('%d.%m.%Y %H:%M') if practice.created_at else '',
        'created_date': practice.created_date.strftime('%d.%m.%Y'),
    }

    return render(request, 'admin_panel/practices/form.html', {
        'practice': practice_data,
        'categories': categories,
        'page_title': f'Редактирование: {practice.title}',
        'admin_name': request.session.get('admin_name', 'Администратор'),
    })


@csrf_exempt
def practice_delete(request, practice_id):
    """Удаление практики"""
    if not check_admin_access(request):
        return redirect('admin_panel:admin_login')

    if request.method == 'POST':
        practice = get_object_or_404(Practice, id=practice_id)

        if practice.file and os.path.isfile(practice.file.path):
            os.remove(practice.file.path)

        practice.delete()
        messages.success(request, 'Практика успешно удалена')

    return redirect('admin_panel:practices_list')