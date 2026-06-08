from django.core.management.base import BaseCommand
from events.models import EventFormat, ActivityType, Subject


class Command(BaseCommand):
    help = 'Инициализация справочных данных для мероприятий'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Начинаю заполнение справочников мероприятий...'))

        # Форматы проведения (Таблица 14)
        formats = [
            'Очные мероприятия (оффлайн)',
            'Дистанционные мероприятия (онлайн)',
            'Гибридные форматы',
        ]

        created_count = 0
        for name in formats:
            obj, created = EventFormat.objects.get_or_create(name=name)
            if created:
                created_count += 1
                self.stdout.write(f'  Создан формат: {name}')

        self.stdout.write(self.style.SUCCESS(f'Добавлено форматов: {created_count}'))

        # Типы активности (Таблица 13)
        activity_types = [
            'Вебинар',
            'Конкурс',
            'Конференция',
            'Круглый стол',
            'Курсы повышения квалификации',
            'Мастер-класс',
            'Олимпиада',
            'Открытый урок',
            'Семинар',
            'Слет',
            'Тренинг',
            'Форум',
        ]

        created_count = 0
        for name in activity_types:
            obj, created = ActivityType.objects.get_or_create(name=name)
            if created:
                created_count += 1
                self.stdout.write(f'  Создан тип активности: {name}')

        self.stdout.write(self.style.SUCCESS(f'Добавлено типов активности: {created_count}'))

        # Предметные области (Таблица 15)
        subjects = [
            'Биология',
            'География',
            'Дошкольное образование',
            'ИЗО',
            'Иностранные языки',
            'Информатика',
            'История',
            'Математика',
            'Межпредметные направления',
            'Музыка',
            'Начальные классы',
            'Обществознание',
            'Русский язык и литература',
            'Физика',
            'Физическая культура',
            'Химия',
            'Подходит всем',
        ]

        created_count = 0
        for name in subjects:
            obj, created = Subject.objects.get_or_create(name=name)
            if created:
                created_count += 1
                self.stdout.write(f'  Создана предметная область: {name}')

        self.stdout.write(self.style.SUCCESS(f'Добавлено предметных областей: {created_count}'))
        self.stdout.write(self.style.SUCCESS('Справочники мероприятий успешно заполнены!'))