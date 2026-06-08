from django.db import models
from .constants import *

# Импортируем реальные модели из основных приложений
from news.models import News as RealNews
from news.models import TargetAudience, ContentType, InfoStatus, NewsPhoto

from events.models import Event as RealEvent
from events.models import EventFormat, ActivityType, Subject, EventPhoto

from materials.models import Material as RealMaterial
from materials.models import MaterialType, DifficultyLevel, Grade, WorkFormat, AssessmentSystem, AdditionalCategory

from documents.models import Document as RealDocument
from documents.models import DocumentCategory, ActionLevel

from surveys.models import Survey as RealSurvey
from surveys.models import SurveyCategory, ActivityStatus, QuestionType, Question as RealQuestion
from surveys.models import AnswerOption as RealAnswerOption
from surveys.models import SurveyPassing as RealSurveyPassing
from surveys.models import TeacherAnswer as RealTeacherAnswer


# ========== ПРОКСИ-МОДЕЛИ ДЛЯ НОВОСТЕЙ ==========
class News(models.Model):
    """Прокси-модель для новостей в админке"""
    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'
        managed = False
        db_table = 'news'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.real_news = None

    @property
    def title(self):
        return self.real_news.title if self.real_news else ''

    @property
    def short_description(self):
        return self.real_news.short_description if self.real_news else ''

    @property
    def full_description(self):
        return self.real_news.detailed_description if self.real_news else ''

    @property
    def publish_date(self):
        return self.real_news.publication_date if self.real_news else None

    @property
    def status(self):
        return self.real_news.info_status.name if self.real_news and self.real_news.info_status else ''

    @property
    def content_type(self):
        return self.real_news.content_type.name if self.real_news and self.real_news.content_type else ''

    @property
    def target_audience(self):
        return self.real_news.target_audience.name if self.real_news and self.real_news.target_audience else ''

    @property
    def created_at(self):
        return self.real_news.created_at if self.real_news else None

    @property
    def updated_at(self):
        return self.real_news.updated_at if self.real_news else None

    @property
    def is_published(self):
        return self.real_news.is_published if self.real_news else False

    def __str__(self):
        return self.title


# ========== ПРОКСИ-МОДЕЛИ ДЛЯ МЕРОПРИЯТИЙ ==========
class Event(models.Model):
    """Прокси-модель для мероприятий в админке"""
    class Meta:
        verbose_name = 'Мероприятие'
        verbose_name_plural = 'Мероприятия'
        managed = False
        db_table = 'event'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.real_event = None

    @property
    def title(self):
        return self.real_event.title if self.real_event else ''

    @property
    def short_description(self):
        return self.real_event.short_description if self.real_event else ''

    @property
    def full_description(self):
        return self.real_event.detailed_description if self.real_event else ''

    @property
    def date(self):
        return self.real_event.date if self.real_event else None

    @property
    def time(self):
        return self.real_event.time if self.real_event else None

    @property
    def date_time_display(self):
        if self.real_event:
            return f"{self.real_event.date} {self.real_event.time}"
        return ''

    @property
    def location(self):
        return self.real_event.location if self.real_event else ''

    @property
    def subject(self):
        return self.real_event.subject.name if self.real_event and self.real_event.subject else ''

    @property
    def format(self):
        return self.real_event.format.name if self.real_event and self.real_event.format else ''

    @property
    def activity_type(self):
        return self.real_event.activity_type.name if self.real_event and self.real_event.activity_type else ''

    @property
    def target_audience(self):
        return self.real_event.target_audience.name if self.real_event and self.real_event.target_audience else ''

    @property
    def created_at(self):
        return self.real_event.created_at if self.real_event else None

    @property
    def updated_at(self):
        return self.real_event.updated_at if self.real_event else None

    def __str__(self):
        return self.title


# ========== ПРОКСИ-МОДЕЛИ ДЛЯ МАТЕРИАЛОВ ==========
class MethodMaterial(models.Model):
    """Прокси-модель для методических материалов в админке"""
    class Meta:
        verbose_name = 'Методический материал'
        verbose_name_plural = 'Методические материалы'
        managed = False
        db_table = 'material'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.real_material = None

    @property
    def title(self):
        return self.real_material.title if self.real_material else ''

    @property
    def short_description(self):
        return self.real_material.description if self.real_material else ''

    @property
    def subject(self):
        return self.real_material.subject.name if self.real_material and self.real_material.subject else ''

    @property
    def material_type(self):
        return self.real_material.material_type.name if self.real_material and self.real_material.material_type else ''

    @property
    def difficulty(self):
        return self.real_material.difficulty.name if self.real_material and self.real_material.difficulty else ''

    @property
    def grade(self):
        return self.real_material.grade.name if self.real_material and self.real_material.grade else ''

    @property
    def format(self):
        return self.real_material.format.name if self.real_material and self.real_material.format else ''

    @property
    def assessment(self):
        return self.real_material.assessment.name if self.real_material and self.real_material.assessment else ''

    @property
    def additional(self):
        return self.real_material.additional.name if self.real_material and self.real_material.additional else ''

    @property
    def file(self):
        return self.real_material.file if self.real_material else None

    @property
    def created_at(self):
        return self.real_material.created_at if self.real_material else None

    def __str__(self):
        return self.title


# ========== ПРОКСИ-МОДЕЛИ ДЛЯ ДОКУМЕНТОВ ==========
class NormativeDocument(models.Model):
    """Прокси-модель для нормативных документов в админке"""
    class Meta:
        verbose_name = 'Нормативный документ'
        verbose_name_plural = 'Нормативные документы'
        managed = False
        db_table = 'document'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.real_document = None

    @property
    def title(self):
        return self.real_document.title if self.real_document else ''

    @property
    def short_description(self):
        return self.real_document.description if self.real_document else ''

    @property
    def full_description(self):
        return self.real_document.full_description if self.real_document else ''

    @property
    def publish_date(self):
        return self.real_document.publication_date if self.real_document else None

    @property
    def file_size(self):
        return self.real_document.file_size if self.real_document else 0

    @property
    def file_size_display(self):
        return self.real_document.file_size_display if self.real_document else '0 КБ'

    @property
    def category(self):
        return self.real_document.category.name if self.real_document and self.real_document.category else ''

    @property
    def level(self):
        return self.real_document.level.name if self.real_document and self.real_document.level else ''

    @property
    def year(self):
        return self.real_document.publication_date.year if self.real_document else None

    @property
    def file(self):
        return self.real_document.file if self.real_document else None

    @property
    def created_at(self):
        return self.real_document.created_at if self.real_document else None

    def __str__(self):
        return self.title


# ========== ПРОКСИ-МОДЕЛИ ДЛЯ ОПРОСОВ ==========
class Survey(models.Model):
    """Прокси-модель для опросов в админке"""
    class Meta:
        verbose_name = 'Опрос'
        verbose_name_plural = 'Опросы'
        managed = False
        db_table = 'survey'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.real_survey = None

    @property
    def title(self):
        return self.real_survey.title if self.real_survey else ''

    @property
    def short_description(self):
        return self.real_survey.description if self.real_survey else ''

    @property
    def category(self):
        return self.real_survey.category.name if self.real_survey and self.real_survey.category else ''

    @property
    def duration(self):
        return self.real_survey.duration if self.real_survey else ''

    @property
    def status(self):
        return self.real_survey.status.name if self.real_survey and self.real_survey.status else ''

    @property
    def questions_count(self):
        return self.real_survey.questions_count if self.real_survey else 0

    @property
    def deadline(self):
        return self.real_survey.deadline if self.real_survey else None

    @property
    def created_date(self):
        return self.real_survey.created_date if self.real_survey else None

    @property
    def created_at(self):
        return self.real_survey.created_at if self.real_survey else None

    @property
    def updated_at(self):
        return self.real_survey.updated_at if self.real_survey else None

    @property
    def is_published(self):
        return self.real_survey.is_published if self.real_survey else False

    @property
    def status_code(self):
        return self.real_survey.status_code if self.real_survey else 'completed'

    @property
    def status_display(self):
        return self.real_survey.status_display if self.real_survey else 'Завершен'

    def __str__(self):
        return self.title


class Question(models.Model):
    """Прокси-модель для вопросов в админке"""
    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'
        managed = False
        db_table = 'question'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.real_question = None

    @property
    def text(self):
        return self.real_question.text if self.real_question else ''

    @property
    def question_type(self):
        return self.real_question.question_type.name if self.real_question and self.real_question.question_type else ''

    @property
    def question_type_id(self):
        return self.real_question.question_type.id if self.real_question and self.real_question.question_type else None

    @property
    def order(self):
        return self.real_question.order if self.real_question else 0

    @property
    def is_required(self):
        return self.real_question.is_required if self.real_question else True

    @property
    def survey(self):
        return self.real_question.survey if self.real_question else None

    def __str__(self):
        return self.text[:50] if self.text else ''


class AnswerOption(models.Model):
    """Прокси-модель для вариантов ответов в админке"""
    class Meta:
        verbose_name = 'Вариант ответа'
        verbose_name_plural = 'Варианты ответов'
        managed = False
        db_table = 'answer_option'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.real_option = None

    @property
    def text(self):
        return self.real_option.text if self.real_option else ''

    @property
    def order(self):
        return self.real_option.order if self.real_option else 0

    @property
    def question(self):
        return self.real_option.question if self.real_option else None

    def __str__(self):
        return self.text[:30] if self.text else ''


class QuestionType(models.Model):
    """Прокси-модель для типов вопросов в админке"""
    class Meta:
        verbose_name = 'Тип вопроса'
        verbose_name_plural = 'Типы вопросов'
        managed = False
        db_table = 'question_type'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.real_type = None

    @property
    def name(self):
        return self.real_type.name if self.real_type else ''

    def __str__(self):
        return self.name


class SurveyCategory(models.Model):
    """Прокси-модель для категорий опросов в админке"""
    class Meta:
        verbose_name = 'Категория опроса'
        verbose_name_plural = 'Категории опросов'
        managed = False
        db_table = 'survey_category'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.real_category = None

    @property
    def name(self):
        return self.real_category.name if self.real_category else ''

    @property
    def bg_color(self):
        return self.real_category.bg_color if self.real_category else 'rgba(201, 228, 202, 0.85)'

    @property
    def text_color(self):
        return self.real_category.text_color if self.real_category else '#1e5128'

    def __str__(self):
        return self.name


class ActivityStatus(models.Model):
    """Прокси-модель для статусов активности в админке"""
    class Meta:
        verbose_name = 'Статус активности'
        verbose_name_plural = 'Статусы активности'
        managed = False
        db_table = 'activity_status'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.real_status = None

    @property
    def name(self):
        return self.real_status.name if self.real_status else ''

    def __str__(self):
        return self.name


from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class AdminUser(models.Model):
    """Модель для администраторов платформы"""
    email = models.EmailField(max_length=200, unique=True, verbose_name='Email (логин)')
    name = models.CharField(max_length=200, verbose_name='Имя администратора')
    password = models.CharField(max_length=255, verbose_name='Пароль')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'admin_users'
        verbose_name = 'Администратор'
        verbose_name_plural = 'Администраторы'

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return f"{self.name} ({self.email})"