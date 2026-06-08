from django.db import models
from django.utils import timezone
from news.models import TargetAudience  # Переиспользуем из новостей


class EventFormat(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='Идентификатор формата проведения')
    name = models.CharField(max_length=100, verbose_name='Название')

    class Meta:
        db_table = 'event_format'
        verbose_name = 'Формат проведения'
        verbose_name_plural = 'Форматы проведения'
        ordering = ['name']

    def __str__(self):
        return self.name


class ActivityType(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='Идентификатор типа активности')
    name = models.CharField(max_length=100, verbose_name='Название')

    class Meta:
        db_table = 'activity_type'
        verbose_name = 'Тип активности'
        verbose_name_plural = 'Типы активности'
        ordering = ['name']

    def __str__(self):
        return self.name


class Subject(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='Идентификатор предметной области')
    name = models.CharField(max_length=100, verbose_name='Название')

    class Meta:
        db_table = 'subject'
        verbose_name = 'Предметная область'
        verbose_name_plural = 'Предметные области'
        ordering = ['name']

    def __str__(self):
        return self.name


class Event(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='Идентификатор мероприятия')
    target_audience = models.ForeignKey(
        TargetAudience,
        on_delete=models.PROTECT,
        db_column='target_audience_id',
        verbose_name='Целевая аудитория'
    )
    format = models.ForeignKey(
        EventFormat,
        on_delete=models.PROTECT,
        db_column='format_id',
        verbose_name='Формат проведения'
    )
    activity_type = models.ForeignKey(
        ActivityType,
        on_delete=models.PROTECT,
        db_column='activity_type_id',
        verbose_name='Тип активности'
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.PROTECT,
        db_column='subject_id',
        verbose_name='Предметная область'
    )

    # Основные поля
    title = models.CharField(max_length=100, verbose_name='Название')
    short_description = models.CharField(max_length=250, verbose_name='Краткое описание')
    detailed_description = models.TextField(max_length=5000, verbose_name='Подробное описание')  # ← ИЗМЕНЕНО С 3000 НА 5000
    date = models.DateField(verbose_name='Дата проведения')
    time = models.TimeField(verbose_name='Время проведения')
    location = models.CharField(max_length=100, verbose_name='Место проведения')

    # Дополнительные поля
    participants = models.PositiveIntegerField(default=0, verbose_name='Участников')
    max_participants = models.PositiveIntegerField(default=100, verbose_name='Макс. участников')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    is_published = models.BooleanField(default=True, verbose_name='Опубликовано')

    class Meta:
        db_table = 'event'
        verbose_name = 'Мероприятие'
        verbose_name_plural = 'Мероприятия'
        ordering = ['date', 'title']

    def __str__(self):
        return self.title

    @property
    def is_completed(self):
        """Проверка, завершено ли мероприятие"""
        from django.utils import timezone
        return self.date < timezone.now().date()


class EventPhoto(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='Идентификатор фото')
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        db_column='event_id',
        related_name='photos',
        verbose_name='Мероприятие'
    )
    photo = models.ImageField(
        upload_to='events/photos/',
        verbose_name='Фотография',
        blank=True,
        null=True
    )

    class Meta:
        db_table = 'event_photo'
        verbose_name = 'Фотография мероприятия'
        verbose_name_plural = 'Фотографии мероприятий'

    def __str__(self):
        return f"Фото {self.id} для мероприятия {self.event_id}"