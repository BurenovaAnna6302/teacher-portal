from django.db import models
from django.utils import timezone


class TargetAudience(models.Model):
    """
    Целевая аудитория (Таблица 16 из диплома)
    """
    id = models.AutoField(primary_key=True, verbose_name='Идентификатор целевой аудитории')
    name = models.CharField(max_length=100, verbose_name='Название')

    class Meta:
        db_table = 'target_audience'
        verbose_name = 'Целевая аудитория'
        verbose_name_plural = 'Целевые аудитории'
        ordering = ['name']

    def __str__(self):
        return self.name


class ContentType(models.Model):
    """
    Тип контента (Таблица 17 из диплома)
    """
    id = models.AutoField(primary_key=True, verbose_name='Идентификатор типа контента')
    name = models.CharField(max_length=100, verbose_name='Название')

    class Meta:
        db_table = 'content_type'
        verbose_name = 'Тип контента'
        verbose_name_plural = 'Типы контента'
        ordering = ['name']

    def __str__(self):
        return self.name


class InfoStatus(models.Model):
    """
    Статус информации (Таблица 18 из диплома)
    """
    id = models.AutoField(primary_key=True, verbose_name='Идентификатор статуса информации')
    name = models.CharField(max_length=100, verbose_name='Название')

    class Meta:
        db_table = 'info_status'
        verbose_name = 'Статус информации'
        verbose_name_plural = 'Статусы информации'
        ordering = ['name']

    def __str__(self):
        return self.name


class News(models.Model):
    """
    Новость (Таблица 2 из диплома)
    """
    id = models.AutoField(primary_key=True, verbose_name='Идентификатор новости')

    # Внешние ключи
    target_audience = models.ForeignKey(
        TargetAudience,
        on_delete=models.PROTECT,
        db_column='target_audience_id',
        verbose_name='Целевая аудитория'
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.PROTECT,
        db_column='content_type_id',
        verbose_name='Тип контента'
    )
    info_status = models.ForeignKey(
        InfoStatus,
        on_delete=models.PROTECT,
        db_column='info_status_id',
        verbose_name='Статус информации'
    )

    # Основные поля
    title = models.CharField(max_length=100, verbose_name='Название')
    short_description = models.CharField(max_length=250, verbose_name='Краткое описание')
    detailed_description = models.TextField(max_length=5000, verbose_name='Подробное описание')
    publication_date = models.DateField(default=timezone.now, verbose_name='Дата публикации')

    # Дополнительные поля
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    is_published = models.BooleanField(default=True, verbose_name='Опубликовано')

    class Meta:
        db_table = 'news'
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'
        ordering = ['-publication_date']

    def __str__(self):
        return self.title


class NewsPhoto(models.Model):
    """
    Фотография новости (Таблица 31 из диплома)
    """
    id = models.AutoField(primary_key=True, verbose_name='Идентификатор фото')
    news = models.ForeignKey(
        News,
        on_delete=models.CASCADE,
        db_column='news_id',
        related_name='photos',
        verbose_name='Новость'
    )
    photo = models.ImageField(
        upload_to='news/photos/',  # Папка для загрузки фото
        verbose_name='Фотография',
        blank=True,
        null=True
    )

    class Meta:
        db_table = 'news_photo'
        verbose_name = 'Фотография новости'
        verbose_name_plural = 'Фотографии новостей'

    def __str__(self):
        return f"Фото {self.id} для новости {self.news_id}"