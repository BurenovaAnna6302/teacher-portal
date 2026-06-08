from django.core.management.base import BaseCommand
from django.core.files import File
from documents.models import Document, DocumentCategory, ActionLevel
from datetime import datetime, timedelta
from pathlib import Path
import random


class Command(BaseCommand):
    help = 'Создание тестовых нормативных документов'

    def get_category_color(self, category_name):
        """Возвращает цвет для категории"""
        colors = {
            'ФГОС': 'rgba(184, 212, 232, 0.85)',
            'Федеральные законы': 'rgba(201, 228, 202, 0.85)',
            'Приказы': 'rgba(232, 212, 240, 0.85)',
            'Методические рекомендации': 'rgba(245, 213, 184, 0.85)',
            'Профстандарты': 'rgba(212, 232, 240, 0.85)',
            'Локальные акты': 'rgba(255, 228, 196, 0.85)',
            'Санитарные нормы': 'rgba(220, 220, 235, 0.85)',
        }
        return colors.get(category_name, 'rgba(200, 200, 200, 0.85)')

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Начинаю создание нормативных документов...'))

        # Получаем все справочники
        categories = {c.name: c for c in DocumentCategory.objects.all()}
        levels = {l.name: l for l in ActionLevel.objects.all()}

        # Данные для документов
        documents_data = [
            {
                'title': 'Федеральный государственный образовательный стандарт основного общего образования',
                'description': 'Утвержден приказом Министерства просвещения Российской Федерации от 31 мая 2021 г. № 287',
                'category': 'ФГОС',
                'level': 'Федеральный',
                'year': 2021,
                'month': 5,
                'day': 31,
                'file_size': 2_300_000,  # 2.3 МБ
            },
            {
                'title': "Федеральный закон 'Об образовании в Российской Федерации'",
                'description': '№ 273-ФЗ от 29 декабря 2012 года с последними изменениями 2024 года',
                'category': 'Федеральные законы',
                'level': 'Федеральный',
                'year': 2024,
                'month': 1,
                'day': 9,
                'file_size': 4_100_000,  # 4.1 МБ
            },
            {
                'title': 'Методические рекомендации по организации внеурочной деятельности',
                'description': 'Рекомендации Министерства просвещения РФ для образовательных организаций',
                'category': 'Методические рекомендации',
                'level': 'Федеральный',
                'year': 2023,
                'month': 8,
                'day': 15,
                'file_size': 1_800_000,  # 1.8 МБ
            },
            {
                'title': "Профессиональный стандарт 'Педагог'",
                'description': 'Профессиональный стандарт педагога (педагогическая деятельность в сфере дошкольного, начального общего, основного общего, среднего общего образования)',
                'category': 'Профстандарты',
                'level': 'Федеральный',
                'year': 2023,
                'month': 10,
                'day': 18,
                'file_size': 987_000,  # 987 КБ
            },
            {
                'title': 'Приказ об утверждении федерального перечня учебников',
                'description': 'Приказ Министерства просвещения РФ об утверждении федерального перечня учебников на 2024-2025 учебный год',
                'category': 'Приказы',
                'level': 'Федеральный',
                'year': 2024,
                'month': 2,
                'day': 21,
                'file_size': 3_500_000,  # 3.5 МБ
            },
            {
                'title': 'Региональные требования к аттестации педагогических работников',
                'description': 'Положение о порядке аттестации педагогических работников в Московской области',
                'category': 'Приказы',
                'level': 'Региональный',
                'year': 2023,
                'month': 3,
                'day': 10,
                'file_size': 1_200_000,  # 1.2 МБ
            },
            {
                'title': 'ФГОС среднего общего образования',
                'description': 'Федеральный государственный образовательный стандарт среднего общего образования (10-11 классы)',
                'category': 'ФГОС',
                'level': 'Федеральный',
                'year': 2022,
                'month': 8,
                'day': 12,
                'file_size': 2_100_000,  # 2.1 МБ
            },
            {
                'title': 'Методические рекомендации по работе с одаренными детьми',
                'description': 'Методические материалы для педагогов по выявлению и развитию одаренности у обучающихся',
                'category': 'Методические рекомендации',
                'level': 'Федеральный',
                'year': 2024,
                'month': 5,
                'day': 5,
                'file_size': 1_500_000,  # 1.5 МБ
            },
            {
                'title': 'Положение об организации образовательного процесса',
                'description': 'Локальный нормативный акт образовательной организации по вопросам организации учебного процесса',
                'category': 'Локальные акты',
                'level': 'Локальный',
                'year': 2024,
                'month': 9,
                'day': 1,
                'file_size': 856_000,  # 856 КБ
            },
            {
                'title': 'ФГОС начального общего образования',
                'description': 'Федеральный государственный образовательный стандарт начального общего образования (1-4 классы)',
                'category': 'ФГОС',
                'level': 'Федеральный',
                'year': 2021,
                'month': 5,
                'day': 31,
                'file_size': 1_900_000,  # 1.9 МБ
            },
            {
                'title': 'Санитарные правила и нормы СанПиН для школ',
                'description': 'СанПиН 2.4.3648-20 "Санитарно-эпидемиологические требования к организациям воспитания и обучения"',
                'category': 'Санитарные нормы',
                'level': 'Федеральный',
                'year': 2020,
                'month': 9,
                'day': 28,
                'file_size': 3_200_000,  # 3.2 МБ
            },
            {
                'title': 'Методические рекомендации по инклюзивному образованию',
                'description': 'Практические рекомендации для педагогов по работе с детьми с ограниченными возможностями здоровья',
                'category': 'Методические рекомендации',
                'level': 'Федеральный',
                'year': 2023,
                'month': 4,
                'day': 20,
                'file_size': 2_400_000,  # 2.4 МБ
            },
        ]

        # Путь к папке с файлами
        files_folder = Path('documents/static/documents/files')
        files_folder.mkdir(parents=True, exist_ok=True)

        self.stdout.write(self.style.WARNING(f'📁 Папка для файлов: {files_folder.absolute()}'))

        # Удаляем старые документы
        Document.objects.all().delete()
        self.stdout.write(self.style.WARNING('🧹 Старые документы удалены'))

        # Создаем документы
        created_count = 0
        for i, data in enumerate(documents_data, 1):
            # Проверяем существование всех справочников
            if data['category'] not in categories:
                self.stdout.write(self.style.ERROR(f'  ❌ Категория "{data["category"]}" не найдена!'))
                continue

            if data['level'] not in levels:
                self.stdout.write(self.style.ERROR(f'  ❌ Уровень "{data["level"]}" не найден!'))
                continue

            category = categories[data['category']]
            level = levels[data['level']]

            # Создаем документ
            # При создании документа:
            document = Document.objects.create(
                category=category,
                level=level,
                title=data['title'],
                description=data['description'],
                publication_date=datetime(data['year'], data['month'], data['day']).date(),
                file_size=data['file_size'],
                is_published=True
            )

            # Ищем файл
            file_found = False
            possible_names = [
                files_folder / f'{i}.pdf',
                files_folder / f'{i}.docx',
                files_folder / f'{i}.doc',
                files_folder / f'doc_{i}.pdf',
            ]

            for file_path in possible_names:
                if file_path.exists():
                    try:
                        with open(file_path, 'rb') as f:
                            document.file.save(file_path.name, File(f))
                        self.stdout.write(f'  ✅ [{i}] Создан документ + файл: {data["title"][:30]}...')
                        file_found = True
                        break
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'  ❌ [{i}] Ошибка загрузки файла: {str(e)}'))

            if not file_found:
                self.stdout.write(f'  ⚠️ [{i}] Создан документ БЕЗ файла: {data["title"][:30]}...')

            created_count += 1

        self.stdout.write(self.style.SUCCESS(f'✅ Успешно создано {created_count} документов!'))

        files_count = Document.objects.exclude(file__isnull=True).count()
        self.stdout.write(self.style.SUCCESS(f'📄 Загружено файлов: {files_count}'))