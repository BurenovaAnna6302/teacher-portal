from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.utils import timezone
import json
from datetime import datetime
from .models import Survey, SurveyCategory, ActivityStatus, Question, AnswerOption, SurveyPassing, TeacherAnswer
import uuid


def surveys_list(request):
    """
    Страница списка опросов – только активные опросы (статус = 'Активные').
    """
    # Получаем все справочники из БД
    categories = SurveyCategory.objects.all()
    statuses = ActivityStatus.objects.all()

    # Длительности для фильтра (статические)
    durations = [
        {'id': 1, 'name': 'До 10 мин'},
        {'id': 2, 'name': '10-15 мин'},
        {'id': 3, 'name': 'Более 15 мин'},
    ]

    # Определяем ID активного статуса (поиск по части названия "актив")
    try:
        active_status = ActivityStatus.objects.get(name__icontains='актив')
        active_status_id = active_status.id
    except ActivityStatus.DoesNotExist:
        # Если не найден, пробуем по умолчанию id=1 (чаще всего активный статус имеет id=1)
        active_status_id = 1

    # Получаем ТОЛЬКО активные опросы (опубликованные и с активным статусом)
    surveys_queryset = Survey.objects.filter(
        is_published=True,
        status_id=active_status_id
    ).select_related(
        'category', 'status'
    ).order_by('-created_date')

    paginator = Paginator(surveys_queryset, 12)
    first_page = paginator.get_page(1)

    # Подготовка данных для первой страницы (для JavaScript)
    first_page_data = []
    for survey in first_page:
        first_page_data.append({
            'id': survey.id,
            'title': survey.title,
            'description': survey.description,
            'questions_count': survey.questions_count,
            'duration': survey.duration,
            'deadline': survey.deadline.strftime('%d.%m.%Y') if survey.deadline else None,
            'created_date': survey.created_date.strftime('%Y-%m-%d'),
            'status_code': 'active',
            'status_display': 'Активен',
            'category': {
                'id': survey.category.id,
                'name': survey.category.name,
                'bg_color': survey.category.bg_color,
                'text_color': survey.category.text_color,
            },
        })

    # Подготовка контекста
    context = {
        'surveys': first_page,
        'categories': categories,
        'durations': durations,
        'statuses': statuses,
        'current_page': 1,
        'total_pages': paginator.num_pages,

        # JSON для JavaScript
        'categories_json': json.dumps({
            str(c.id): {
                'id': c.id,
                'name': c.name,
                'bg_color': c.bg_color,
                'text_color': c.text_color,
            } for c in categories
        }, ensure_ascii=False),

        'durations_json': json.dumps({
            str(d['id']): d for d in durations
        }, ensure_ascii=False),

        'statuses_json': json.dumps({
            str(s.id): {
                'id': s.id,
                'name': s.name,
            } for s in statuses
        }, ensure_ascii=False),

        'surveys_json': json.dumps(first_page_data, ensure_ascii=False),
    }

    return render(request, 'surveys/surveys.html', context)


def surveys_list_api(request):
    """
    API для AJAX-запросов.
    Возвращает JSON с отфильтрованными активными опросами (статус = 'Активные').
    """
    # Получаем параметры из GET-запроса
    page = request.GET.get('page', 1)

    # Получаем фильтры
    category_filter = request.GET.getlist('category')
    duration_filter = request.GET.getlist('duration')
    status_filter = request.GET.getlist('status')  # пока не используется, т.к. только активные

    # Определяем ID активного статуса
    try:
        active_status = ActivityStatus.objects.get(name__icontains='актив')
        active_status_id = active_status.id
    except ActivityStatus.DoesNotExist:
        active_status_id = 1

    # Базовый запрос – только активные опросы (опубликованные и с активным статусом)
    surveys_queryset = Survey.objects.filter(
        is_published=True,
        status_id=active_status_id
    ).select_related('category', 'status')

    # Применяем фильтр по категории
    if category_filter:
        surveys_queryset = surveys_queryset.filter(category_id__in=category_filter)

    # Фильтр по длительности (на основе извлечения минут из строки)
    if duration_filter:
        duration_conditions = []
        for duration_id in duration_filter:
            duration_id = int(duration_id)
            if duration_id == 1:      # До 10 мин
                duration_conditions.append('До 10')
            elif duration_id == 2:    # 10-15 мин
                duration_conditions.append('10-15')
            elif duration_id == 3:    # Более 15 мин
                duration_conditions.append('20')

        if duration_conditions:
            query = Q()
            for condition in duration_conditions:
                query |= Q(duration__icontains=condition)
            surveys_queryset = surveys_queryset.filter(query)

    # Фильтр по статусу (оставлен для совместимости, но активные уже отобраны)
    if status_filter:
        # Здесь можно было бы добавить завершённые, но по задаче показываем только активные
        pass

    # Сортировка по дате (новые сверху)
    surveys_queryset = surveys_queryset.order_by('-created_date')

    # Пагинация
    paginator = Paginator(surveys_queryset, 12)
    current_page = paginator.get_page(page)

    # Формируем данные для JSON
    surveys_data = []
    for survey in current_page:
        surveys_data.append({
            'id': survey.id,
            'title': survey.title,
            'description': survey.description,
            'questions_count': survey.questions_count,
            'duration': survey.duration,
            'deadline': survey.deadline.strftime('%d.%m.%Y') if survey.deadline else None,
            'created_date': survey.created_date.strftime('%Y-%m-%d'),
            'status_code': 'active',
            'status_display': 'Активен',
            'category': {
                'id': survey.category.id,
                'name': survey.category.name,
                'bg_color': survey.category.bg_color,
                'text_color': survey.category.text_color,
            },
        })

    return JsonResponse({
        'surveys': surveys_data,
        'total_pages': paginator.num_pages,
        'current_page': int(page),
        'has_next': current_page.has_next(),
        'has_previous': current_page.has_previous(),
        'total_items': paginator.count,
    })


def survey_detail(request, survey_id):
    """
    Детальная страница опроса с вопросами.
    Доступна только для активных опросов (статус = 'Активные' и is_published=True).
    """
    # Определяем ID активного статуса
    try:
        active_status = ActivityStatus.objects.get(name__icontains='актив')
        active_status_id = active_status.id
    except ActivityStatus.DoesNotExist:
        active_status_id = 1

    # Проверяем, что опрос опубликован и имеет активный статус
    survey = get_object_or_404(
        Survey,
        id=survey_id,
        is_published=True,
        status_id=active_status_id
    )

    # Получаем вопросы с вариантами ответов
    questions = survey.questions.all().order_by('order').prefetch_related('options', 'question_type')

    questions_data = []
    for question in questions:
        options = question.options.all().order_by('order')
        questions_data.append({
            'id': question.id,
            'text': question.text,
            'order': question.order,
            'is_required': question.is_required,
            'question_type': {
                'id': question.question_type.id,
                'name': question.question_type.name,
            },
            'options': options,
        })

    context = {
        'survey': survey,
        'questions': questions_data,
        'page_title': survey.title,
    }

    return render(request, 'surveys/survey_detail.html', context)


@csrf_exempt
def submit_survey(request, survey_id):
    """
    Обработка отправки опроса (анонимно).
    Доступна только для активных опросов.
    """
    if request.method == 'POST':
        # Определяем ID активного статуса
        try:
            active_status = ActivityStatus.objects.get(name__icontains='актив')
            active_status_id = active_status.id
        except ActivityStatus.DoesNotExist:
            active_status_id = 1

        # Проверяем, что опрос активен и опубликован
        survey = get_object_or_404(
            Survey,
            id=survey_id,
            is_published=True,
            status_id=active_status_id
        )

        session_key = f'survey_{survey_id}_completed'
        if request.session.get(session_key):
            messages.error(request, 'Вы уже проходили этот опрос')
            return redirect('surveys:survey_detail', survey_id=survey_id)

        # Создаём прохождение (анонимное)
        passing = SurveyPassing.objects.create(
            survey=survey,
            teacher=None,
            status='completed'
        )

        # Обрабатываем ответы
        questions = survey.questions.all().prefetch_related('question_type', 'options')
        for question in questions:
            field_name = f'question_{question.id}'
            answer = TeacherAnswer.objects.create(
                passing=passing,
                question=question
            )

            if question.question_type.id == 1:  # Открытый вопрос
                text_answer = request.POST.get(field_name, '')
                if text_answer:
                    answer.text_answer = text_answer
                    answer.save()

            elif question.question_type.id == 2:  # Одиночный выбор
                option_id = request.POST.get(field_name)
                if option_id:
                    try:
                        option = AnswerOption.objects.get(id=option_id)
                        answer.selected_option = option
                        answer.save()
                    except AnswerOption.DoesNotExist:
                        pass

            elif question.question_type.id == 3:  # Множественный выбор
                option_ids = request.POST.getlist(field_name)
                if option_ids:
                    options = AnswerOption.objects.filter(id__in=option_ids)
                    answer.selected_options.set(options)

        request.session[session_key] = True
        messages.success(request, 'Спасибо! Ваши ответы успешно сохранены.')
        return redirect('surveys:survey_detail', survey_id=survey_id)

    return redirect('surveys:survey_detail', survey_id=survey_id)


def survey_results(request, survey_id):
    """
    Просмотр результатов опроса (для администратора).
    Доступ без проверки активности.
    """
    survey = get_object_or_404(Survey, id=survey_id)

    passings = survey.passings.all()
    total_participants = passings.count()

    questions_stats = []
    for question in survey.questions.all().order_by('order'):
        stats = {
            'question': question,
            'answers_count': TeacherAnswer.objects.filter(question=question).count(),
        }

        if question.question_type.id in [2, 3]:
            options_stats = []
            for option in question.options.all():
                if question.question_type.id == 2:
                    count = TeacherAnswer.objects.filter(
                        question=question,
                        selected_option=option
                    ).count()
                else:
                    count = TeacherAnswer.objects.filter(
                        question=question,
                        selected_options=option
                    ).count()

                percentage = round((count / total_participants) * 100, 1) if total_participants > 0 else 0
                options_stats.append({
                    'option': option,
                    'count': count,
                    'percentage': percentage
                })
            stats['options_stats'] = options_stats

        if question.question_type.id == 1:
            text_answers = TeacherAnswer.objects.filter(
                question=question
            ).exclude(text_answer='').values_list('text_answer', flat=True)
            stats['text_answers'] = list(text_answers)

        questions_stats.append(stats)

    context = {
        'survey': survey,
        'total_participants': total_participants,
        'passings': passings,
        'questions_stats': questions_stats,
    }

    return render(request, 'surveys/survey_results.html', context)