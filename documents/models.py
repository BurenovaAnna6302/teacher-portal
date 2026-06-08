from django.db import models
from django.utils import timezone


class DocumentCategory(models.Model):
    """
    Категория документа (Таблица 20 из диплома)
    """
    id = models.AutoField(primary_key=True, verbose_name='Идентификатор категории документа')
    name = models.CharField(max_length=100, verbose_name='Название')
    bg_color = models.CharField(max_length=50, verbose_name='Цвет фона', default='rgba(184, 212, 232, 0.85)')
    text_color = models.CharField(max_length=50, verbose_name='Цвет текста', default='#0c4a6e')

    class Meta:
        db_table = 'document_category'
        verbose_name = 'Категория документа'
        verbose_name_plural = 'Категории документов'
        ordering = ['name']

    def __str__(self):
        return self.name


class ActionLevel(models.Model):
    """
    Уровень действия (Таблица 19 из диплома)
    """
    id = models.AutoField(primary_key=True, verbose_name='Идентификатор уровня действия')
    name = models.CharField(max_length=100, verbose_name='Название')

    class Meta:
        db_table = 'action_level'
        verbose_name = 'Уровень действия'
        verbose_name_plural = 'Уровни действия'
        ordering = ['id']

    def __str__(self):
        return self.name


class Document(models.Model):
    """
    Нормативный документ (Таблица 6 из диплома)
    """
    id = models.AutoField(primary_key=True, verbose_name='Идентификатор документа')

    # Внешние ключи
    category = models.ForeignKey(
        DocumentCategory,
        on_delete=models.PROTECT,
        db_column='category_id',
        verbose_name='Категория документа'
    )
    level = models.ForeignKey(
        ActionLevel,
        on_delete=models.PROTECT,
        db_column='level_id',
        verbose_name='Уровень действия'
    )

    # Основные поля
    title = models.CharField(max_length=100, verbose_name='Название')
    description = models.CharField(max_length=250, verbose_name='Краткое описание')
    publication_date = models.DateField(default=timezone.now, verbose_name='Дата публикации')
    file_size = models.IntegerField(verbose_name='Размер файла (в байтах)', default=0)
    file = models.FileField(
        upload_to='documents/',
        verbose_name='Файл документа',
        blank=True,
        null=True
    )

    # Дополнительные поля
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    is_published = models.BooleanField(default=True, verbose_name='Опубликовано')

    class Meta:
        db_table = 'document'
        verbose_name = 'Нормативный документ'
        verbose_name_plural = 'Нормативные документы'
        ordering = ['-publication_date']

    def __str__(self):
        return self.title

    @property
    def file_size_display(self):
        """Возвращает размер файла в читаемом формате"""
        size = self.file_size
        if size < 1024:
            return f"{size} Б"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} КБ"
        elif size < 1024 * 1024 * 1024:
            return f"{size / (1024 * 1024):.1f} МБ"
        else:
            return f"{size / (1024 * 1024 * 1024):.1f} ГБ"

    @property
    def year(self):
        """Возвращает год публикации"""
        return str(self.publication_date.year)

    @property
    def date_display(self):
        """Форматированная дата публикации"""
        months = {
            1: 'января', 2: 'февраля', 3: 'марта', 4: 'апреля',
            5: 'мая', 6: 'июня', 7: 'июля', 8: 'августа',
            9: 'сентября', 10: 'октября', 11: 'ноября', 12: 'декабря'
        }
        return f"{self.publication_date.day} {months[self.publication_date.month]} {self.publication_date.year}"