from django.core.management.base import BaseCommand
from django.core.files import File
from materials.models import (
    Material, Subject, MaterialType, DifficultyLevel, Grade,
    WorkFormat, AssessmentSystem, AdditionalCategory
)
from datetime import datetime, timedelta
from pathlib import Path
import random


class Command(BaseCommand):
    help = 'Создание тестовых методических материалов'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Начинаю создание методических материалов...'))

        # Получаем все справочники
        subjects = {s.name: s for s in Subject.objects.all()}
        types = {t.name: t for t in MaterialType.objects.all()}
        difficulties = {d.name: d for d in DifficultyLevel.objects.all()}
        grades = {g.name: g for g in Grade.objects.all()}
        formats = {f.name: f for f in WorkFormat.objects.all()}
        assessments = {a.name: a for a in AssessmentSystem.objects.all()}
        additionals = {a.name: a for a in AdditionalCategory.objects.all()}

        # Данные для материалов
        materials_data = [
            {
                'title': 'Квантовая физика: основные принципы',
                'description': 'Подробный конспект урока по квантовой физике с практическими примерами и задачами для углубленного изучения.',
                'subject': 'Физика',
                'type': 'Конспекты уроков',
                'difficulty': 'Углубленное изучение',
                'grade': '10-11 классы',
                'format': 'Фронтальная работа',
                'assessment': 'С критериальным оцениванием',
                'additional': 'Подготовка к экзаменам',
                'duration': '90 минут',
                'days_ago': 15,
            },
            {
                'title': 'Интерактивная игра "Цифры и счет"',
                'description': 'Игровое занятие для дошкольников по изучению цветов с использованием авторской методики.',
                'subject': 'Дошкольное образование',
                'type': 'Интерактивные задания',
                'difficulty': 'Базовый уровень',
                'grade': 'Дошкольное образование',
                'format': 'Групповая работа',
                'assessment': 'С системой зачет/незачет',
                'additional': 'Внеурочная деятельность',
                'duration': '25 минут',
                'days_ago': 20,
            },
            {
                'title': 'Лабораторная работа: Синтез веществ',
                'description': 'Лабораторная работа по органической химии с пошаговой инструкцией и требованиями безопасности.',
                'subject': 'Химия',
                'type': 'Лабораторные работы',
                'difficulty': 'Продвинутый уровень',
                'grade': '10-11 классы',
                'format': 'Парная работа',
                'assessment': 'С балльной системой',
                'additional': 'Экспериментальные разработки',
                'duration': '90 минут',
                'days_ago': 18,
            },
            {
                'title': 'Презентация: История Средних веков',
                'description': 'Мультимедийная презентация с иллюстрациями и видеофрагментами по истории средневековья.',
                'subject': 'История и обществознание',
                'type': 'Презентации',
                'difficulty': 'Базовый уровень',
                'grade': '7-9 классы',
                'format': 'Фронтальная работа',
                'assessment': 'С самооценкой',
                'additional': 'К праздничным датам',
                'duration': '45 минут',
                'days_ago': 12,
            },
            {
                'title': 'Тест по биологии: Генетика',
                'description': 'Контрольный тест по разделу генетики с заданиями разного уровня сложности.',
                'subject': 'Биология',
                'type': 'Тесты и контрольные работы',
                'difficulty': 'Продвинутый уровень',
                'grade': '10-11 классы',
                'format': 'Индивидуальная работа',
                'assessment': 'С балльной системой',
                'additional': 'Подготовка к экзаменам',
                'duration': '40 минут',
                'days_ago': 10,
            },
            {
                'title': 'Проект: Мой родной край',
                'description': 'Творческий проект по изучению географии родного края с элементами исследовательской работы.',
                'subject': 'География',
                'type': 'Творческие проекты',
                'difficulty': 'Базовый уровень',
                'grade': '5-6 классы',
                'format': 'Проектная деятельность',
                'assessment': 'С взаимопроверкой',
                'additional': 'Краеведческие материалы',
                'duration': '120 минут',
                'days_ago': 8,
            },
            {
                'title': 'Видеоурок: Английская грамматика',
                'description': 'Видеоурок по английской грамматике с примерами и упражнениями для закрепления материала.',
                'subject': 'Иностранные языки',
                'type': 'Видеоуроки',
                'difficulty': 'Базовый уровень',
                'grade': '5-6 классы',
                'format': 'Дистанционное обучение',
                'assessment': 'С самооценкой',
                'additional': 'Авторские методики',
                'duration': '30 минут',
                'days_ago': 5,
            },
            {
                'title': 'Дидактические материалы по информатике',
                'description': 'Комплект дидактических материалов по программированию для подготовки к олимпиадам.',
                'subject': 'Информатика и ИКТ',
                'type': 'Дидактические материалы',
                'difficulty': 'Углубленное изучение',
                'grade': '10-11 классы',
                'format': 'Смешанное обучение',
                'assessment': 'С критериальным оцениванием',
                'additional': 'Подготовка к олимпиадам',
                'duration': '60 минут',
                'days_ago': 3,
            },
            {
                'title': 'Занятие для дошкольников: Изучаем цвета',
                'description': 'Игровое занятие для дошкольников по изучению цветов с использованием авторской методики.',
                'subject': 'Дошкольное образование',
                'type': 'Сценарии уроков',
                'difficulty': 'Базовый уровень',
                'grade': 'Дошкольное образование',
                'format': 'Групповая работа',
                'assessment': 'С системой зачет/незачет',
                'additional': 'Авторские методики',
                'duration': '25 минут',
                'days_ago': 1,
            },
            {
                'title': 'Практикум по решению задач на движение',
                'description': 'Практические задания различной сложности по теме "Задачи на движение" с подробными решениями.',
                'subject': 'Математика',
                'type': 'Практикумы',
                'difficulty': 'Продвинутый уровень',
                'grade': '7-9 классы',
                'format': 'Индивидуальная работа',
                'assessment': 'С балльной системой',
                'additional': 'Подготовка к экзаменам',
                'duration': '60 минут',
                'days_ago': 28,
            },
            {
                'title': 'Раздаточные материалы: Правила пунктуации',
                'description': 'Карточки и схемы по основным правилам пунктуации с примерами и упражнениями для закрепления.',
                'subject': 'Русский язык и литература',
                'type': 'Раздаточные материалы',
                'difficulty': 'Базовый уровень',
                'grade': '5-6 классы',
                'format': 'Фронтальная работа',
                'assessment': 'С самооценкой',
                'additional': 'Материалы для замены уроков',
                'duration': '45 минут',
                'days_ago': 25,
            },
            {
                'title': 'Аудиокурс: Разговорный немецкий',
                'description': 'Аудиокурс разговорного немецкого языка с диалогами и упражнениями для развития навыков восприятия речи.',
                'subject': 'Иностранные языки',
                'type': 'Аудиоматериалы',
                'difficulty': 'Продвинутый уровень',
                'grade': '10-11 классы',
                'format': 'Дистанционное обучение',
                'assessment': 'С взаимопроверкой',
                'additional': 'Авторские методики',
                'duration': '50 минут',
                'days_ago': 22,
            },
            {
                'title': 'Конспект: Основы безопасности жизнедеятельности',
                'description': 'Конспект урока по основам безопасности в чрезвычайных ситуациях с практическими заданиями.',
                'subject': 'ОБЖ',
                'type': 'Конспекты уроков',
                'difficulty': 'Базовый уровень',
                'grade': '7-9 классы',
                'format': 'Фронтальная работа',
                'assessment': 'С системой зачет/незачет',
                'additional': 'Сезонные материалы',
                'duration': '45 минут',
                'days_ago': 20,
            },
            {
                'title': 'Тренажер по художественной композиции',
                'description': 'Интерактивный тренажер для развития навыков композиции и цветового решения в изобразительном искусстве.',
                'subject': 'ИЗО и музыка',
                'type': 'Интерактивные задания',
                'difficulty': 'Углубленное изучение',
                'grade': '5-6 классы',
                'format': 'Индивидуальная работа',
                'assessment': 'С критериальным оцениванием',
                'additional': 'Подготовка к олимпиадам',
                'duration': '60 минут',
                'days_ago': 18,
            },
            {
                'title': 'Мастер-класс: Робототехника для начинающих',
                'description': 'Видео мастер-класс по основам робототехники с пошаговой сборкой простого робота.',
                'subject': 'Технология',
                'type': 'Видеоуроки',
                'difficulty': 'Базовый уровень',
                'grade': '7-9 классы',
                'format': 'Проектная деятельность',
                'assessment': 'С взаимопроверкой',
                'additional': 'Профориентационные уроки',
                'duration': '75 минут',
                'days_ago': 15,
            },
            {
                'title': 'Спортивная эстафета: Олимпийские игры',
                'description': 'Сценарий спортивного мероприятия в формате олимпийских игр с эстафетами и командными играми.',
                'subject': 'Физическая культура',
                'type': 'Сценарии уроков',
                'difficulty': 'Базовый уровень',
                'grade': '1-4 классы',
                'format': 'Групповая работа',
                'assessment': 'С системой зачет/незачет',
                'additional': 'К праздничным датам',
                'duration': '90 минут',
                'days_ago': 12,
            },
        ]

        # Путь к папке с файлами (можно положить примерные PDF)
        files_folder = Path('materials/static/materials/files')
        files_folder.mkdir(parents=True, exist_ok=True)

        self.stdout.write(self.style.WARNING(f'📁 Папка для файлов: {files_folder.absolute()}'))

        # Удаляем старые материалы
        Material.objects.all().delete()
        self.stdout.write(self.style.WARNING('🧹 Старые материалы удалены'))

        # Создаем материалы
        created_count = 0
        for i, data in enumerate(materials_data, 1):
            # Проверяем существование всех справочников
            if data['subject'] not in subjects:
                self.stdout.write(self.style.ERROR(f'  ❌ Предмет "{data["subject"]}" не найден!'))
                continue

            if data['type'] not in types:
                self.stdout.write(self.style.ERROR(f'  ❌ Тип "{data["type"]}" не найден!'))
                continue

            if data['difficulty'] not in difficulties:
                self.stdout.write(self.style.ERROR(f'  ❌ Сложность "{data["difficulty"]}" не найдена!'))
                continue

            if data['grade'] not in grades:
                self.stdout.write(self.style.ERROR(f'  ❌ Класс "{data["grade"]}" не найден!'))
                continue

            if data['format'] not in formats:
                self.stdout.write(self.style.ERROR(f'  ❌ Формат "{data["format"]}" не найден!'))
                continue

            if data['assessment'] not in assessments:
                self.stdout.write(self.style.ERROR(f'  ❌ Оценка "{data["assessment"]}" не найдена!'))
                continue

            if data['additional'] not in additionals:
                self.stdout.write(self.style.ERROR(f'  ❌ Категория "{data["additional"]}" не найдена!'))
                continue

            # Создаем материал
            material = Material.objects.create(
                subject=subjects[data['subject']],
                material_type=types[data['type']],
                difficulty=difficulties[data['difficulty']],
                grade=grades[data['grade']],
                format=formats[data['format']],
                assessment=assessments[data['assessment']],
                additional=additionals[data['additional']],
                title=data['title'],
                description=data['description'],
                duration=data['duration'],
                created_at=datetime.now() - timedelta(days=data['days_ago']),
                is_published=True
            )

            # Ищем файл (можно создать примерный PDF или оставить None)
            file_found = False
            possible_names = [
                files_folder / f'{i}.pdf',
                files_folder / f'{i}.docx',
                files_folder / f'{i}.doc',
                files_folder / f'material_{i}.pdf',
            ]

            for file_path in possible_names:
                if file_path.exists():
                    try:
                        with open(file_path, 'rb') as f:
                            material.file.save(file_path.name, File(f))
                        self.stdout.write(f'  ✅ [{i}] Создан материал + файл: {data["title"][:30]}...')
                        file_found = True
                        break
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'  ❌ [{i}] Ошибка загрузки файла: {str(e)}'))

            if not file_found:
                self.stdout.write(f'  ⚠️ [{i}] Создан материал БЕЗ файла: {data["title"][:30]}...')

            created_count += 1

        self.stdout.write(self.style.SUCCESS(f'✅ Успешно создано {created_count} материалов!'))

        files_count = Material.objects.exclude(file__isnull=True).count()
        self.stdout.write(self.style.SUCCESS(f'📄 Загружено файлов: {files_count}'))