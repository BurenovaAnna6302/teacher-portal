from django.db import models
from django.utils import timezone


class PracticeCategory(models.Model):
    """Категория успешной практики"""
    name = models.CharField(max_length=100, verbose_name='Название категории')
    icon = models.CharField(max_length=50, default='fas fa-star', verbose_name='Иконка')
    icon_color = models.CharField(max_length=20, default='#3b82f6', verbose_name='Цвет иконки')
    sort_order = models.IntegerField(default=0, verbose_name='Порядок сортировки')

    class Meta:
        db_table = 'practice_category'
        verbose_name = 'Категория практики'
        verbose_name_plural = 'Категории практик'
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name


class Practice(models.Model):
    """Успешная практика"""

    AUDIENCE_CHOICES = [
        ('young', 'Молодые педагоги (до 3 лет)'),
        ('experienced', 'Опытные педагоги'),
        ('all', 'Все категории'),
    ]

    FORMAT_CHOICES = [
        ('single', 'Опыт одного педагога'),
        ('methodological', 'Опыт методического объединения'),
        ('school', 'Школьный проект'),
        ('municipal', 'Муниципальный опыт'),
        ('regional', 'Региональный опыт'),
    ]

    DIFFICULTY_CHOICES = [
        ('easy', 'Лёгкий'),
        ('medium', 'Средний'),
        ('hard', 'Сложный'),
    ]

    DIFFICULTY_COLORS = {
        'easy': '#10b981',
        'medium': '#f59e0b',
        'hard': '#ef4444',
    }

    DIFFICULTY_ICONS = {
        'easy': 'fas fa-leaf',
        'medium': 'fas fa-chart-simple',
        'hard': 'fas fa-mountain',
    }

    # Основные поля
    category = models.ForeignKey(
        PracticeCategory,
        on_delete=models.PROTECT,
        related_name='practices',
        verbose_name='Категория',
        db_index=True  # Добавлен индекс
    )
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    short_description = models.CharField(max_length=250, verbose_name='Краткое описание')
    full_description = models.TextField(blank=True, verbose_name='Полное описание')

    # Дополнительные поля - ОБЯЗАТЕЛЬНЫЕ с индексами
    audience = models.CharField(max_length=20, choices=AUDIENCE_CHOICES, verbose_name='Целевая аудитория', db_index=True)
    format_type = models.CharField(max_length=20, choices=FORMAT_CHOICES, verbose_name='Формат практики', db_index=True)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, verbose_name='Уровень сложности', db_index=True)

    # Файл для скачивания (необязательный)
    file = models.FileField(upload_to='practices/files/', blank=True, null=True, verbose_name='Файл')

    # Системные поля с индексами
    created_date = models.DateField(default=timezone.now, verbose_name='Дата публикации', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    is_published = models.BooleanField(default=True, verbose_name='Опубликовано', db_index=True)

    class Meta:
        db_table = 'practice'
        verbose_name = 'Успешная практика'
        verbose_name_plural = 'Успешные практики'
        ordering = ['-created_date']
        # Добавляем составной индекс для частых запросов
        indexes = [
            models.Index(fields=['is_published', '-created_date']),
            models.Index(fields=['category', 'is_published']),
        ]

    def __str__(self):
        return self.title

    @property
    def published_date_display(self):
        months = {
            1: 'января', 2: 'февраля', 3: 'марта', 4: 'апреля',
            5: 'мая', 6: 'июня', 7: 'июля', 8: 'августа',
            9: 'сентября', 10: 'октября', 11: 'ноября', 12: 'декабря'
        }
        return f"{self.created_date.day} {months[self.created_date.month]} {self.created_date.year}"

    @property
    def difficulty_color(self):
        return self.DIFFICULTY_COLORS.get(self.difficulty, '#6b7280')

    @property
    def difficulty_icon(self):
        return self.DIFFICULTY_ICONS.get(self.difficulty, 'fas fa-chart-line')

    @property
    def audience_display(self):
        for value, label in self.AUDIENCE_CHOICES:
            if value == self.audience:
                return label
        return ''

    @property
    def format_display(self):
        for value, label in self.FORMAT_CHOICES:
            if value == self.format_type:
                return label
        return ''

    @property
    def difficulty_display(self):
        for value, label in self.DIFFICULTY_CHOICES:
            if value == self.difficulty:
                return label
        return ''