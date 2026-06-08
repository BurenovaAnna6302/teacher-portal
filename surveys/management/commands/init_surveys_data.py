# init_surveys_data
from django.core.management.base import BaseCommand
from surveys.models import SurveyCategory, ActivityStatus, QuestionType


class Command(BaseCommand):
    help = 'Инициализация справочных данных для опросов'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Начинаю заполнение справочников опросов...'))

        # Категории опросов (Таблица 22)
        categories_data = [
            {'name': 'Потребности', 'bg_color': 'rgba(201, 228, 202, 0.85)', 'text_color': '#1e5128'},
            {'name': 'Обратная связь', 'bg_color': 'rgba(184, 212, 232, 0.85)', 'text_color': '#0c4a6e'},
            {'name': 'Планирование', 'bg_color': 'rgba(232, 212, 240, 0.85)', 'text_color': '#6b21a8'},
            {'name': 'Технологии', 'bg_color': 'rgba(245, 213, 184, 0.85)', 'text_color': '#c2410c'},
            {'name': 'Методика', 'bg_color': 'rgba(212, 232, 240, 0.85)', 'text_color': '#075985'},
        ]

        created_count = 0
        for data in categories_data:
            obj, created = SurveyCategory.objects.get_or_create(
                name=data['name'],
                defaults={'bg_color': data['bg_color'], 'text_color': data['text_color']}
            )
            if created:
                created_count += 1
                self.stdout.write(f'  Создана категория: {data["name"]}')

        self.stdout.write(self.style.SUCCESS(f'Добавлено категорий: {created_count}'))

        # Статусы активности (Таблица 21)
        statuses_data = [
            'Активные',
            'Завершенные',
        ]

        created_count = 0
        for name in statuses_data:
            obj, created = ActivityStatus.objects.get_or_create(name=name)
            if created:
                created_count += 1
                self.stdout.write(f'  Создан статус: {name}')

        self.stdout.write(self.style.SUCCESS(f'Добавлено статусов: {created_count}'))

        # Типы вопросов (Таблица 23) - ИСПРАВЛЕНО
        question_types = [
            'Открытый вопрос',           # Для текстового ответа
            'Одиночный выбор',            # Для выбора одного варианта
            'Множественный выбор',        # Для выбора нескольких вариантов
        ]

        created_count = 0
        for name in question_types:
            obj, created = QuestionType.objects.get_or_create(name=name)
            if created:
                created_count += 1
                self.stdout.write(f'  Создан тип вопроса: {name}')

        self.stdout.write(self.style.SUCCESS(f'Добавлено типов вопросов: {created_count}'))
        self.stdout.write(self.style.SUCCESS('Справочники опросов успешно заполнены!'))