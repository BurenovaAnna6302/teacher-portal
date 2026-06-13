from django.shortcuts import render
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import Q
import json
from .models import (
    Material, Subject, MaterialType, DifficultyLevel, Grade,
    WorkFormat, AssessmentSystem, AdditionalCategory
)


def materials_list(request):
    """
    Страница списка методических материалов - только первая загрузка.
    Без сортировки - порядок по ID (как в базе данных)
    """

    subjects = Subject.objects.all()
    types = MaterialType.objects.all()
    difficulty = DifficultyLevel.objects.all()
    grades = Grade.objects.all()
    formats = WorkFormat.objects.all()
    assessment = AssessmentSystem.objects.all()
    additional = AdditionalCategory.objects.all()

    # Базовый запрос - БЕЗ СОРТИРОВКИ
    materials_queryset = Material.objects.filter(is_published=True).select_related(
        'subject', 'material_type', 'difficulty', 'grade', 'format', 'assessment', 'additional'
    )

    # ИЗМЕНЕНО: 8 материалов на странице
    paginator = Paginator(materials_queryset, 12)
    first_page = paginator.get_page(1)

    first_page_data = []
    for material in first_page:
        # ИСПРАВЛЕНО: Безопасные проверки для всех связанных полей
        first_page_data.append({
            'id': material.id,
            'title': material.title,
            'description': material.description,
            'file_url': material.file.url if material.file else None,
            'date_added': material.date_added,
            'duration': material.duration,
            'subject': {
                'id': material.subject.id if material.subject else None,
                'name': material.subject.name if material.subject else 'Не указана',
                'bg_color': material.subject.bg_color if material.subject and hasattr(material.subject, 'bg_color') else 'rgba(184, 212, 232, 0.85)',
                'text_color': material.subject.text_color if material.subject and hasattr(material.subject, 'text_color') else '#0c4a6e',
            },
            'type': {
                'id': material.material_type.id if material.material_type else None,
                'name': material.material_type.name if material.material_type else 'Не указан',
                'bg_color': material.material_type.bg_color if material.material_type and hasattr(material.material_type, 'bg_color') else 'rgba(201, 228, 202, 0.85)',
                'text_color': material.material_type.text_color if material.material_type and hasattr(material.material_type, 'text_color') else '#1e5128',
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
                'name': material.assessment.name if material.assessment else 'Не указана',
            },
            'additional': {
                'id': material.additional.id if material.additional else None,
                'name': material.additional.name if material.additional else 'Не указана',
            },
        })

    context = {
        'materials': first_page,
        'subjects': subjects,
        'types': types,
        'difficulty': difficulty,
        'grades': grades,
        'formats': formats,
        'assessment': assessment,
        'additional': additional,
        'current_page': 1,
        'total_pages': paginator.num_pages,

        'subjects_json': json.dumps({
            str(s.id): {
                'id': s.id,
                'name': s.name,
                'bg_color': s.bg_color,
                'text_color': s.text_color,
            } for s in subjects
        }, ensure_ascii=False),

        'types_json': json.dumps({
            str(t.id): {
                'id': t.id,
                'name': t.name,
                'bg_color': t.bg_color,
                'text_color': t.text_color,
            } for t in types
        }, ensure_ascii=False),

        'difficulty_json': json.dumps({
            str(d.id): {
                'id': d.id,
                'name': d.name,
            } for d in difficulty
        }, ensure_ascii=False),

        'grades_json': json.dumps({
            str(g.id): {
                'id': g.id,
                'name': g.name,
            } for g in grades
        }, ensure_ascii=False),

        'formats_json': json.dumps({
            str(f.id): {
                'id': f.id,
                'name': f.name,
            } for f in formats
        }, ensure_ascii=False),

        'assessment_json': json.dumps({
            str(a.id): {
                'id': a.id,
                'name': a.name,
            } for a in assessment
        }, ensure_ascii=False),

        'additional_json': json.dumps({
            str(ad.id): {
                'id': ad.id,
                'name': ad.name,
            } for ad in additional
        }, ensure_ascii=False),

        'materials_json': json.dumps(first_page_data, ensure_ascii=False),
    }

    return render(request, 'materials/materials.html', context)


def materials_list_api(request):
    """
    API для AJAX-запросов.
    Возвращает JSON с отфильтрованными материалами.
    """

    page = request.GET.get('page', 1)
    sort = request.GET.get('sort', 'none')

    # Получаем фильтры
    subject_filter = request.GET.getlist('subject[]')
    if not subject_filter:
        subject_filter = request.GET.getlist('subject')

    type_filter = request.GET.getlist('type[]')
    if not type_filter:
        type_filter = request.GET.getlist('type')

    difficulty_filter = request.GET.getlist('difficulty[]')
    if not difficulty_filter:
        difficulty_filter = request.GET.getlist('difficulty')

    grade_filter = request.GET.getlist('grade[]')
    if not grade_filter:
        grade_filter = request.GET.getlist('grade')

    format_filter = request.GET.getlist('format[]')
    if not format_filter:
        format_filter = request.GET.getlist('format')

    assessment_filter = request.GET.getlist('assessment[]')
    if not assessment_filter:
        assessment_filter = request.GET.getlist('assessment')

    additional_filter = request.GET.getlist('additional[]')
    if not additional_filter:
        additional_filter = request.GET.getlist('additional')

    # Базовый запрос
    materials_queryset = Material.objects.filter(is_published=True).select_related(
        'subject', 'material_type', 'difficulty', 'grade', 'format', 'assessment', 'additional'
    )

    # Применяем фильтры
    if subject_filter:
        materials_queryset = materials_queryset.filter(subject_id__in=subject_filter)

    if type_filter:
        materials_queryset = materials_queryset.filter(material_type_id__in=type_filter)

    if difficulty_filter:
        materials_queryset = materials_queryset.filter(difficulty_id__in=difficulty_filter)

    if grade_filter:
        materials_queryset = materials_queryset.filter(grade_id__in=grade_filter)

    if format_filter:
        materials_queryset = materials_queryset.filter(format_id__in=format_filter)

    if assessment_filter:
        materials_queryset = materials_queryset.filter(assessment_id__in=assessment_filter)

    if additional_filter:
        materials_queryset = materials_queryset.filter(additional_id__in=additional_filter)

    # Применяем сортировку
    if sort == 'date-desc':
        materials_queryset = materials_queryset.order_by('-created_at')
    elif sort == 'date-asc':
        materials_queryset = materials_queryset.order_by('created_at')
    elif sort == 'title-asc':
        materials_queryset = materials_queryset.order_by('title')
    elif sort == 'title-desc':
        materials_queryset = materials_queryset.order_by('-title')

    paginator = Paginator(materials_queryset, 12)
    current_page = paginator.get_page(page)

    # Формируем данные для JSON
    materials_data = []
    for material in current_page:
        # ИСПРАВЛЕНО: Безопасные проверки для всех связанных полей
        materials_data.append({
            'id': material.id,
            'title': material.title,
            'description': material.description,
            'file_url': material.file.url if material.file else None,
            'date_added': material.date_added,
            'duration': material.duration,
            'subject': {
                'id': material.subject.id if material.subject else None,
                'name': material.subject.name if material.subject else 'Не указана',
                'bg_color': material.subject.bg_color if material.subject and hasattr(material.subject, 'bg_color') else 'rgba(184, 212, 232, 0.85)',
                'text_color': material.subject.text_color if material.subject and hasattr(material.subject, 'text_color') else '#0c4a6e',
            },
            'type': {
                'id': material.material_type.id if material.material_type else None,
                'name': material.material_type.name if material.material_type else 'Не указан',
                'bg_color': material.material_type.bg_color if material.material_type and hasattr(material.material_type, 'bg_color') else 'rgba(201, 228, 202, 0.85)',
                'text_color': material.material_type.text_color if material.material_type and hasattr(material.material_type, 'text_color') else '#1e5128',
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
                'name': material.assessment.name if material.assessment else 'Не указана',
            },
            'additional': {
                'id': material.additional.id if material.additional else None,
                'name': material.additional.name if material.additional else 'Не указана',
            },
        })

    return JsonResponse({
        'materials': materials_data,
        'total_pages': paginator.num_pages,
        'current_page': int(page),
        'has_next': current_page.has_next(),
        'has_previous': current_page.has_previous(),
        'total_items': paginator.count,
        'current_sort': sort,
    })