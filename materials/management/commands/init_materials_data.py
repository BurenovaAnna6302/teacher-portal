from django.core.management.base import BaseCommand
from materials.models import (
    Subject, MaterialType, DifficultyLevel, Grade,
    WorkFormat, AssessmentSystem, AdditionalCategory
)


class Command(BaseCommand):
    help = 'Инициализация справочных данных для методических материалов'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Начинаю заполнение справочников материалов...'))

        # Предметные области
        subjects_data = [
            {'name': 'Биология', 'bg_color': 'rgba(201, 228, 202, 0.85)', 'text_color': '#1e5128'},
            {'name': 'География', 'bg_color': 'rgba(184, 212, 232, 0.85)', 'text_color': '#0c4a6e'},
            {'name': 'Дошкольное образование', 'bg_color': 'rgba(232, 212, 240, 0.85)', 'text_color': '#6b21a8'},
            {'name': 'ИЗО и музыка', 'bg_color': 'rgba(245, 213, 184, 0.85)', 'text_color': '#c2410c'},
            {'name': 'Иностранные языки', 'bg_color': 'rgba(212, 232, 240, 0.85)', 'text_color': '#075985'},
            {'name': 'Информатика и ИКТ', 'bg_color': 'rgba(184, 212, 232, 0.85)', 'text_color': '#0c4a6e'},
            {'name': 'История и обществознание', 'bg_color': 'rgba(240, 232, 212, 0.85)', 'text_color': '#92400e'},
            {'name': 'Математика', 'bg_color': 'rgba(201, 228, 202, 0.85)', 'text_color': '#1e5128'},
            {'name': 'Начальные классы', 'bg_color': 'rgba(232, 212, 240, 0.85)', 'text_color': '#6b21a8'},
            {'name': 'ОБЖ', 'bg_color': 'rgba(245, 213, 184, 0.85)', 'text_color': '#c2410c'},
            {'name': 'Русский язык и литература', 'bg_color': 'rgba(212, 232, 240, 0.85)', 'text_color': '#075985'},
            {'name': 'Технология', 'bg_color': 'rgba(184, 212, 232, 0.85)', 'text_color': '#0c4a6e'},
            {'name': 'Физика', 'bg_color': 'rgba(240, 232, 212, 0.85)', 'text_color': '#92400e'},
            {'name': 'Физическая культура', 'bg_color': 'rgba(201, 228, 202, 0.85)', 'text_color': '#1e5128'},
            {'name': 'Химия', 'bg_color': 'rgba(232, 212, 240, 0.85)', 'text_color': '#6b21a8'},
        ]

        created_count = 0
        for data in subjects_data:
            obj, created = Subject.objects.get_or_create(
                name=data['name'],
                defaults={'bg_color': data['bg_color'], 'text_color': data['text_color']}
            )
            if created:
                created_count += 1
                self.stdout.write(f'  Создана предметная область: {data["name"]}')

        self.stdout.write(self.style.SUCCESS(f'Добавлено предметных областей: {created_count}'))

        # Типы материалов
        types_data = [
            {'name': 'Аудиоматериалы', 'bg_color': 'rgba(201, 228, 202, 0.85)', 'text_color': '#1e5128'},
            {'name': 'Видеоуроки', 'bg_color': 'rgba(184, 212, 232, 0.85)', 'text_color': '#0c4a6e'},
            {'name': 'Дидактические материалы', 'bg_color': 'rgba(232, 212, 240, 0.85)', 'text_color': '#6b21a8'},
            {'name': 'Интерактивные задания', 'bg_color': 'rgba(245, 213, 184, 0.85)', 'text_color': '#c2410c'},
            {'name': 'Конспекты уроков', 'bg_color': 'rgba(212, 232, 240, 0.85)', 'text_color': '#075985'},
            {'name': 'Лабораторные работы', 'bg_color': 'rgba(184, 212, 232, 0.85)', 'text_color': '#0c4a6e'},
            {'name': 'Практикумы', 'bg_color': 'rgba(240, 232, 212, 0.85)', 'text_color': '#92400e'},
            {'name': 'Презентации', 'bg_color': 'rgba(201, 228, 202, 0.85)', 'text_color': '#1e5128'},
            {'name': 'Раздаточные материалы', 'bg_color': 'rgba(232, 212, 240, 0.85)', 'text_color': '#6b21a8'},
            {'name': 'Сценарии уроков', 'bg_color': 'rgba(245, 213, 184, 0.85)', 'text_color': '#c2410c'},
            {'name': 'Тесты и контрольные работы', 'bg_color': 'rgba(212, 232, 240, 0.85)', 'text_color': '#075985'},
            {'name': 'Творческие проекты', 'bg_color': 'rgba(184, 212, 232, 0.85)', 'text_color': '#0c4a6e'},
        ]

        created_count = 0
        for data in types_data:
            obj, created = MaterialType.objects.get_or_create(
                name=data['name'],
                defaults={'bg_color': data['bg_color'], 'text_color': data['text_color']}
            )
            if created:
                created_count += 1
                self.stdout.write(f'  Создан тип материала: {data["name"]}')

        self.stdout.write(self.style.SUCCESS(f'Добавлено типов материалов: {created_count}'))

        # Уровни сложности
        difficulty_data = [
            'Базовый уровень',
            'Задания для одаренных детей',
            'Инклюзивное образование',
            'Коррекционные задания',
            'Продвинутый уровень',
            'Углубленное изучение',
        ]

        created_count = 0
        for name in difficulty_data:
            obj, created = DifficultyLevel.objects.get_or_create(name=name)
            if created:
                created_count += 1
                self.stdout.write(f'  Создан уровень сложности: {name}')

        self.stdout.write(self.style.SUCCESS(f'Добавлено уровней сложности: {created_count}'))

        # Классы
        grades_data = [
            '1-4 классы',
            '5-6 классы',
            '7-9 классы',
            '10-11 классы',
            'Дошкольное образование',
            'Среднее профессиональное образование',
        ]

        created_count = 0
        for name in grades_data:
            obj, created = Grade.objects.get_or_create(name=name)
            if created:
                created_count += 1
                self.stdout.write(f'  Создан класс: {name}')

        self.stdout.write(self.style.SUCCESS(f'Добавлено классов: {created_count}'))

        # Форматы работы
        formats_data = [
            'Групповая работа',
            'Дистанционное обучение',
            'Индивидуальная работа',
            'Парная работа',
            'Проектная деятельность',
            'Смешанное обучение',
            'Фронтальная работа',
        ]

        created_count = 0
        for name in formats_data:
            obj, created = WorkFormat.objects.get_or_create(name=name)
            if created:
                created_count += 1
                self.stdout.write(f'  Создан формат работы: {name}')

        self.stdout.write(self.style.SUCCESS(f'Добавлено форматов работы: {created_count}'))

        # Системы оценивания
        assessment_data = [
            'С балльной системой',
            'С взаимопроверкой',
            'С критериальным оцениванием',
            'С самооценкой',
            'С системой зачет/незачет',
        ]

        created_count = 0
        for name in assessment_data:
            obj, created = AssessmentSystem.objects.get_or_create(name=name)
            if created:
                created_count += 1
                self.stdout.write(f'  Создана система оценивания: {name}')

        self.stdout.write(self.style.SUCCESS(f'Добавлено систем оценивания: {created_count}'))

        # Дополнительные категории
        additional_data = [
            'Авторские методики',
            'Внеурочная деятельность',
            'К праздничным датам',
            'Краеведческие материалы',
            'Материалы для замены уроков',
            'Подготовка к олимпиадам',
            'Подготовка к экзаменам',
            'Профориентационные уроки',
            'Сезонные материалы',
            'Экспериментальные разработки',
        ]

        created_count = 0
        for name in additional_data:
            obj, created = AdditionalCategory.objects.get_or_create(name=name)
            if created:
                created_count += 1
                self.stdout.write(f'  Создана дополнительная категория: {name}')

        self.stdout.write(self.style.SUCCESS(f'Добавлено дополнительных категорий: {created_count}'))
        self.stdout.write(self.style.SUCCESS('Справочники материалов успешно заполнены!'))