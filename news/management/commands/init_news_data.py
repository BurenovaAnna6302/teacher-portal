from django.core.management.base import BaseCommand
from news.models import TargetAudience, ContentType, InfoStatus


class Command(BaseCommand):
    help = 'Инициализация справочных данных для новостей'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Начинаю заполнение справочников...'))

        # Целевая аудитория (из вашего примера)
        target_audiences = [
            'Наставники',
            'Администрация',
            'Молодые педагоги',
            'Все педагоги',
            'Классные руководители',
            'Предметники',
        ]

        created_count = 0
        for name in target_audiences:
            obj, created = TargetAudience.objects.get_or_create(name=name)
            if created:
                created_count += 1
                self.stdout.write(f'  Создана целевая аудитория: {name}')

        self.stdout.write(self.style.SUCCESS(f'Добавлено целевых аудиторий: {created_count}'))

        # Тип контента (из вашего примера)
        content_types = [
            'Гранты и финансирование',
            'Наука и исследования',
            'Повышение квалификации',
            'Социальная поддержка',
            'Творчество и проекты',
            'Нормативные документы',
        ]

        created_count = 0
        for name in content_types:
            obj, created = ContentType.objects.get_or_create(name=name)
            if created:
                created_count += 1
                self.stdout.write(f'  Создан тип контента: {name}')

        self.stdout.write(self.style.SUCCESS(f'Добавлено типов контента: {created_count}'))

        # Статус информации (из вашего примера)
        info_statuses = [
            'Экстренные',
            'Важные',
            'Новости',
            'Аналитика',
            'Анонсы',
            'Документы',
            'Отчеты',
            'Рекомендации',
        ]

        created_count = 0
        for name in info_statuses:
            obj, created = InfoStatus.objects.get_or_create(name=name)
            if created:
                created_count += 1
                self.stdout.write(f'  Создан статус: {name}')

        self.stdout.write(self.style.SUCCESS(f'Добавлено статусов: {created_count}'))
        self.stdout.write(self.style.SUCCESS('Справочники успешно заполнены!'))