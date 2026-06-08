from django.core.management.base import BaseCommand
from documents.models import DocumentCategory, ActionLevel


class Command(BaseCommand):
    help = 'Инициализация справочных данных для нормативных документов'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Начинаю заполнение справочников документов...'))

        # Категории документов (Таблица 20)
        categories_data = [
            {'name': 'ФГОС', 'bg_color': 'rgba(184, 212, 232, 0.85)', 'text_color': '#0c4a6e'},
            {'name': 'Федеральные законы', 'bg_color': 'rgba(201, 228, 202, 0.85)', 'text_color': '#1e5128'},
            {'name': 'Приказы', 'bg_color': 'rgba(232, 212, 240, 0.85)', 'text_color': '#6b21a8'},
            {'name': 'Методические рекомендации', 'bg_color': 'rgba(245, 213, 184, 0.85)', 'text_color': '#c2410c'},
            {'name': 'Профстандарты', 'bg_color': 'rgba(212, 232, 240, 0.85)', 'text_color': '#075985'},
            {'name': 'Локальные акты', 'bg_color': 'rgba(255, 228, 196, 0.85)', 'text_color': '#92400e'},
            {'name': 'Санитарные нормы', 'bg_color': 'rgba(220, 220, 235, 0.85)', 'text_color': '#4c1d95'},
        ]

        created_count = 0
        for data in categories_data:
            obj, created = DocumentCategory.objects.get_or_create(
                name=data['name'],
                defaults={'bg_color': data['bg_color'], 'text_color': data['text_color']}
            )
            if created:
                created_count += 1
                self.stdout.write(f'  Создана категория: {data["name"]}')

        self.stdout.write(self.style.SUCCESS(f'Добавлено категорий: {created_count}'))

        # Уровни действия (Таблица 19)
        levels_data = [
            'Федеральный',
            'Региональный',
            'Локальный',
        ]

        created_count = 0
        for name in levels_data:
            obj, created = ActionLevel.objects.get_or_create(name=name)
            if created:
                created_count += 1
                self.stdout.write(f'  Создан уровень действия: {name}')

        self.stdout.write(self.style.SUCCESS(f'Добавлено уровней действия: {created_count}'))
        self.stdout.write(self.style.SUCCESS('Справочники документов успешно заполнены!'))