from django.db import models
from teachers.models import Teacher
from materials.models import Material


class Favorite(models.Model):
    """
    Избранный материал (Таблица 5 из диплома)
    """
    id = models.AutoField(primary_key=True, verbose_name='Идентификатор')
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        db_column='teacher_id',
        related_name='favorites',
        verbose_name='Педагог'
    )
    material = models.ForeignKey(
        Material,
        on_delete=models.CASCADE,
        db_column='material_id',
        verbose_name='Материал'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')

    class Meta:
        db_table = 'favorite'
        verbose_name = 'Избранный материал'
        verbose_name_plural = 'Избранные материалы'
        unique_together = ['teacher', 'material']

    def __str__(self):
        return f"Материал {self.material.title} в избранном у {self.teacher}"

    @property
    def added_date_display(self):
        """Форматированная дата добавления"""
        from django.utils import timezone
        now = timezone.now().date()
        delta = now - self.created_at.date()

        if delta.days == 0:
            return 'сегодня'
        elif delta.days == 1:
            return 'вчера'
        elif delta.days < 7:
            return f'{delta.days} дня назад'
        elif delta.days < 30:
            weeks = delta.days // 7
            return f'{weeks} недели назад'
        else:
            months = delta.days // 30
            return f'{months} месяца назад'