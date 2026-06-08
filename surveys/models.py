from django.db import models
from django.utils import timezone

class SurveyCategory(models.Model):
    """Категория опроса"""
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, verbose_name='Название')
    bg_color = models.CharField(max_length=50, verbose_name='Цвет фона', default='rgba(201, 228, 202, 0.85)')
    text_color = models.CharField(max_length=50, verbose_name='Цвет текста', default='#1e5128')

    class Meta:
        db_table = 'survey_category'
        verbose_name = 'Категория опроса'
        verbose_name_plural = 'Категории опросов'
        ordering = ['name']

    def __str__(self):
        return self.name


class ActivityStatus(models.Model):
    """Статус активности"""
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, verbose_name='Название')

    class Meta:
        db_table = 'activity_status'
        verbose_name = 'Статус активности'
        verbose_name_plural = 'Статусы активности'
        ordering = ['id']

    def __str__(self):
        return self.name


class Survey(models.Model):
    """Опрос"""
    id = models.AutoField(primary_key=True)
    category = models.ForeignKey(SurveyCategory, on_delete=models.PROTECT, db_column='category_id', verbose_name='Категория')
    status = models.ForeignKey(ActivityStatus, on_delete=models.PROTECT, db_column='status_id', verbose_name='Статус активности')
    title = models.CharField(max_length=100, verbose_name='Название')
    description = models.CharField(max_length=250, verbose_name='Описание')
    created_date = models.DateField(default=timezone.now, verbose_name='Дата создания')
    duration = models.CharField(max_length=20, verbose_name='Время прохождения', default='10-15 мин')
    questions_count = models.PositiveIntegerField(default=0, verbose_name='Количество вопросов')
    deadline = models.DateField(verbose_name='Дата окончания', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания записи')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    is_published = models.BooleanField(default=True, verbose_name='Опубликовано')

    class Meta:
        db_table = 'survey'
        verbose_name = 'Опрос'
        verbose_name_plural = 'Опросы'
        ordering = ['-created_date']

    def __str__(self):
        return self.title

    @property
    def is_active(self):
        """Активность по статусу из ActivityStatus"""
        if self.status and 'актив' in self.status.name.lower():
            return True
        return False

    @property
    def status_display(self):
        return 'Активен' if self.is_active else 'Завершен'

    @property
    def status_code(self):
        return 'active' if self.is_active else 'completed'

    @property
    def published_date_display(self):
        months = {1: 'января', 2: 'февраля', 3: 'марта', 4: 'апреля',
                  5: 'мая', 6: 'июня', 7: 'июля', 8: 'августа',
                  9: 'сентября', 10: 'октября', 11: 'ноября', 12: 'декабря'}
        return f"{self.created_date.day} {months[self.created_date.month]} {self.created_date.year}"


class QuestionType(models.Model):
    """Тип вопроса"""
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, verbose_name='Название')

    class Meta:
        db_table = 'question_type'
        verbose_name = 'Тип вопроса'
        verbose_name_plural = 'Типы вопросов'
        ordering = ['name']

    def __str__(self):
        return self.name


class Question(models.Model):
    """Вопрос"""
    id = models.AutoField(primary_key=True)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, db_column='survey_id', related_name='questions', verbose_name='Опрос')
    question_type = models.ForeignKey(QuestionType, on_delete=models.PROTECT, db_column='question_type_id', verbose_name='Тип вопроса')
    text = models.CharField(max_length=300, verbose_name='Текст вопроса')
    order = models.PositiveIntegerField(verbose_name='Порядок следования')
    is_required = models.BooleanField(default=True, verbose_name='Обязательный вопрос')

    class Meta:
        db_table = 'question'
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'
        ordering = ['order']

    def __str__(self):
        return f"{self.order}. {self.text[:50]}"


class AnswerOption(models.Model):
    """Вариант ответа"""
    id = models.AutoField(primary_key=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, db_column='question_id', related_name='options', verbose_name='Вопрос')
    text = models.CharField(max_length=200, verbose_name='Текст ответа')
    order = models.PositiveIntegerField(verbose_name='Порядок отображения')

    class Meta:
        db_table = 'answer_option'
        verbose_name = 'Вариант ответа'
        verbose_name_plural = 'Варианты ответов'
        ordering = ['order']

    def __str__(self):
        return f"{self.order}. {self.text[:30]}"


class SurveyPassing(models.Model):
    """Прохождение опроса"""
    STATUS_CHOICES = [('started', 'Начат'), ('in_progress', 'В процессе'), ('completed', 'Завершен')]
    id = models.AutoField(primary_key=True)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, db_column='survey_id', related_name='passings', verbose_name='Опрос')
    teacher = models.ForeignKey('teachers.Teacher', on_delete=models.CASCADE, db_column='teacher_id', verbose_name='Педагог', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='started', verbose_name='Статус прохождения')
    started_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата начала')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата завершения')

    class Meta:
        db_table = 'survey_passing'
        verbose_name = 'Прохождение опроса'
        verbose_name_plural = 'Прохождения опросов'

    def __str__(self):
        return f"Прохождение {self.id} опроса {self.survey_id}"


class TeacherAnswer(models.Model):
    """Ответ педагога"""
    id = models.AutoField(primary_key=True)
    passing = models.ForeignKey(SurveyPassing, on_delete=models.CASCADE, db_column='passing_id', related_name='answers', verbose_name='Прохождение')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, db_column='question_id', verbose_name='Вопрос')
    selected_option = models.ForeignKey(AnswerOption, on_delete=models.CASCADE, db_column='selected_option_id', verbose_name='Выбранный вариант', null=True, blank=True, related_name='single_answers')
    selected_options = models.ManyToManyField(AnswerOption, verbose_name='Выбранные варианты', blank=True, related_name='multiple_answers')
    text_answer = models.TextField(verbose_name='Текстовый ответ', blank=True, max_length=5000)

    class Meta:
        db_table = 'teacher_answer'
        verbose_name = 'Ответ педагога'
        verbose_name_plural = 'Ответы педагогов'
        unique_together = ['passing', 'question']

    def __str__(self):
        return f"Ответ на вопрос {self.question_id}"