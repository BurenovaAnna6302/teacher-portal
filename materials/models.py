from django.db import models
from django.utils import timezone


class Subject(models.Model):
    """
    Предметная область (Таблица 15 из диплома) - для материалов
    """
    id = models.AutoField(primary_key=True, verbose_name='Идентификатор предметной области')
    name = models.CharField(max_length=100, verbose_name='Название')
    bg_color = models.CharField(max_length=50, verbose_name='Цвет фона', default='rgba(184, 212, 232, 0.85)')
    text_color = models.CharField(max_length=50, verbose_name='Цвет текста', default='#0c4a6e')

    class Meta:
        db_table = 'materials_subject'
        verbose_name = 'Предметная область'
        verbose_name_plural = 'Предметные области'
        ordering = ['name']

    def __str__(self):
        return self.name


class MaterialType(models.Model):
    """
    Тип материала (Таблица 24 из диплома)
    """
    id = models.AutoField(primary_key=True, verbose_name='Идентификатор типа материала')
    name = models.CharField(max_length=100, verbose_name='Название')
    bg_color = models.CharField(max_length=50, verbose_name='Цвет фона', default='rgba(201, 228, 202, 0.85)')
    text_color = models.CharField(max_length=50, verbose_name='Цвет текста', default='#1e5128')

    class Meta:
        db_table = 'material_type'
        verbose_name = 'Тип материала'
        verbose_name_plural = 'Типы материалов'
        ordering = ['name']

    def __str__(self):
        return self.name


class DifficultyLevel(models.Model):
    """
    Уровень сложности (Таблица 25 из диплома)
    """
    id = models.AutoField(primary_key=True, verbose_name='Идентификатор уровня сложности')
    name = models.CharField(max_length=100, verbose_name='Название')

    class Meta:
        db_table = 'difficulty_level'
        verbose_name = 'Уровень сложности'
        verbose_name_plural = 'Уровни сложности'
        ordering = ['id']

    def __str__(self):
        return self.name


class Grade(models.Model):
    """
    Класс/возрастная группа (Таблица 26 из диплома)
    """
    id = models.AutoField(primary_key=True, verbose_name='Идентификатор класса')
    name = models.CharField(max_length=100, verbose_name='Название')

    class Meta:
        db_table = 'grade'
        verbose_name = 'Класс'
        verbose_name_plural = 'Классы'
        ordering = ['id']

    def __str__(self):
        return self.name


class WorkFormat(models.Model):
    """
    Формат работы (Таблица 27 из диплома)
    """
    id = models.AutoField(primary_key=True, verbose_name='Идентификатор формата работы')
    name = models.CharField(max_length=100, verbose_name='Название')

    class Meta:
        db_table = 'work_format'
        verbose_name = 'Формат работы'
        verbose_name_plural = 'Форматы работы'
        ordering = ['name']

    def __str__(self):
        return self.name


class AssessmentSystem(models.Model):
    """
    Система оценивания (Таблица 28 из диплома)
    """
    id = models.AutoField(primary_key=True, verbose_name='Идентификатор системы оценивания')
    name = models.CharField(max_length=100, verbose_name='Название')

    class Meta:
        db_table = 'assessment_system'
        verbose_name = 'Система оценивания'
        verbose_name_plural = 'Системы оценивания'
        ordering = ['name']

    def __str__(self):
        return self.name


class AdditionalCategory(models.Model):
    """
    Дополнительная категория (Таблица 29 из диплома)
    """
    id = models.AutoField(primary_key=True, verbose_name='Идентификатор дополнительной категории')
    name = models.CharField(max_length=100, verbose_name='Название')

    class Meta:
        db_table = 'additional_category'
        verbose_name = 'Дополнительная категория'
        verbose_name_plural = 'Дополнительные категории'
        ordering = ['name']

    def __str__(self):
        return self.name


class Material(models.Model):
    """
    Методический материал (Таблица 8 из диплома)
    """
    id = models.AutoField(primary_key=True, verbose_name='Идентификатор материала')

    # Внешние ключи
    subject = models.ForeignKey(
        Subject,
        on_delete=models.PROTECT,
        db_column='subject_id',
        verbose_name='Предметная область'
    )
    material_type = models.ForeignKey(
        MaterialType,
        on_delete=models.PROTECT,
        db_column='material_type_id',
        verbose_name='Тип материала'
    )
    difficulty = models.ForeignKey(
        DifficultyLevel,
        on_delete=models.PROTECT,
        db_column='difficulty_id',
        verbose_name='Уровень сложности'
    )
    grade = models.ForeignKey(
        Grade,
        on_delete=models.PROTECT,
        db_column='grade_id',
        verbose_name='Класс'
    )
    format = models.ForeignKey(
        WorkFormat,
        on_delete=models.PROTECT,
        db_column='format_id',
        verbose_name='Формат работы'
    )
    assessment = models.ForeignKey(
        AssessmentSystem,
        on_delete=models.PROTECT,
        db_column='assessment_id',
        verbose_name='Система оценки'
    )
    # ИСПРАВЛЕНО: добавлены null=True, blank=True
    additional = models.ForeignKey(
        AdditionalCategory,
        on_delete=models.PROTECT,
        db_column='additional_id',
        verbose_name='Дополнительная категория',
        null=True,
        blank=True
    )

    # Основные поля
    title = models.CharField(max_length=100, verbose_name='Название')
    description = models.CharField(max_length=250, verbose_name='Описание')
    file = models.FileField(
        upload_to='materials/',
        verbose_name='Файл',
        blank=True,
        null=True
    )

    # Метаданные
    duration = models.CharField(max_length=50, verbose_name='Длительность', default='45 минут')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    is_published = models.BooleanField(default=True, verbose_name='Опубликовано')

    class Meta:
        db_table = 'material'
        verbose_name = 'Методический материал'
        verbose_name_plural = 'Методические материалы'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def date_added(self):
        """Форматированная дата добавления"""
        months = {
            1: 'января', 2: 'февраля', 3: 'марта', 4: 'апреля',
            5: 'мая', 6: 'июня', 7: 'июля', 8: 'августа',
            9: 'сентября', 10: 'октября', 11: 'ноября', 12: 'декабря'
        }
        return f"{self.created_at.day} {months[self.created_at.month]} {self.created_at.year}"