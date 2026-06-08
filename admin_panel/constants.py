# admin_panel/constants.py
# ========== МЕРОПРИЯТИЯ ==========
EVENT_AUDIENCES = [
    {'id': 1, 'name': 'Начинающие педагоги (0-1 год)', 'value': 'beginner'},
    {'id': 2, 'name': 'Опытные молодые специалисты (1-3 года)', 'value': 'experienced_young'},
    {'id': 3, 'name': 'Педагоги-наставники', 'value': 'mentors'},
    {'id': 4, 'name': 'Руководители методических объединений', 'value': 'leaders'},
]

EVENT_FORMATS = [
    {'id': 1, 'name': 'Очные мероприятия (оффлайн)', 'value': 'offline'},
    {'id': 2, 'name': 'Дистанционные мероприятия (онлайн)', 'value': 'online'},
    {'id': 3, 'name': 'Гибридные форматы', 'value': 'hybrid'},
]

EVENT_ACTIVITY_TYPES = [
    {'id': 1, 'name': 'Вебинар', 'value': 'webinar', 'color': 'rgba(201, 228, 202, 0.85)', 'text_color': '#1e5128'},
    {'id': 2, 'name': 'Конкурс', 'value': 'competition', 'color': 'rgba(184, 212, 232, 0.85)', 'text_color': '#0c4a6e'},
    {'id': 3, 'name': 'Конференция', 'value': 'conference', 'color': 'rgba(232, 212, 240, 0.85)', 'text_color': '#6b21a8'},
    {'id': 4, 'name': 'Круглый стол', 'value': 'round_table', 'color': 'rgba(245, 213, 184, 0.85)', 'text_color': '#c2410c'},
    {'id': 5, 'name': 'Курсы повышения квалификации', 'value': 'training_courses', 'color': 'rgba(212, 232, 240, 0.85)', 'text_color': '#075985'},
    {'id': 6, 'name': 'Мастер-класс', 'value': 'master_class', 'color': 'rgba(240, 232, 212, 0.85)', 'text_color': '#854d0e'},
    {'id': 7, 'name': 'Олимпиада', 'value': 'olympiad', 'color': 'rgba(201, 228, 202, 0.85)', 'text_color': '#1e5128'},
    {'id': 8, 'name': 'Открытый урок', 'value': 'open_lesson', 'color': 'rgba(184, 212, 232, 0.85)', 'text_color': '#0c4a6e'},
    {'id': 9, 'name': 'Семинар', 'value': 'seminar', 'color': 'rgba(232, 212, 240, 0.85)', 'text_color': '#6b21a8'},
    {'id': 10, 'name': 'Слет', 'value': 'meeting', 'color': 'rgba(245, 213, 184, 0.85)', 'text_color': '#c2410c'},
    {'id': 11, 'name': 'Тренинг', 'value': 'training', 'color': 'rgba(212, 232, 240, 0.85)', 'text_color': '#075985'},
    {'id': 12, 'name': 'Форум', 'value': 'forum', 'color': 'rgba(240, 232, 212, 0.85)', 'text_color': '#854d0e'},
]

EVENT_SUBJECTS = [
    {'id': 1, 'name': 'Биология', 'value': 'biology'},
    {'id': 2, 'name': 'География', 'value': 'geography'},
    {'id': 3, 'name': 'Дошкольное образование', 'value': 'preschool'},
    {'id': 4, 'name': 'ИЗО', 'value': 'art'},
    {'id': 5, 'name': 'Иностранные языки', 'value': 'foreign_languages'},
    {'id': 6, 'name': 'Информатика', 'value': 'informatics'},
    {'id': 7, 'name': 'История', 'value': 'history'},
    {'id': 8, 'name': 'Математика', 'value': 'math'},
    {'id': 9, 'name': 'Межпредметные направления', 'value': 'interdisciplinary'},
    {'id': 10, 'name': 'Музыка', 'value': 'music'},
    {'id': 11, 'name': 'Начальные классы', 'value': 'elementary'},
    {'id': 12, 'name': 'Обществознание', 'value': 'social_studies'},
    {'id': 13, 'name': 'Русский язык и литература', 'value': 'russian'},
    {'id': 14, 'name': 'Физика', 'value': 'physics'},
    {'id': 15, 'name': 'Физическая культура', 'value': 'physical_education'},
    {'id': 16, 'name': 'Химия', 'value': 'chemistry'},
    {'id': 17, 'name': 'Подходит всем', 'value': 'all'},
]

# ========== НОВОСТИ ==========
NEWS_STATUSES = [
    {'id': 1, 'name': 'Экстренные', 'value': 'emergency', 'color': 'rgba(255, 200, 200, 0.85)', 'text_color': '#cc0000'},
    {'id': 2, 'name': 'Важные', 'value': 'important', 'color': 'rgba(255, 230, 200, 0.85)', 'text_color': '#ff6600'},
    {'id': 3, 'name': 'Новости', 'value': 'news', 'color': 'rgba(201, 228, 202, 0.85)', 'text_color': '#1e8c1e'},
    {'id': 4, 'name': 'Аналитика', 'value': 'analytics', 'color': 'rgba(200, 220, 240, 0.85)', 'text_color': '#0066cc'},
    {'id': 5, 'name': 'Анонсы', 'value': 'announcements', 'color': 'rgba(240, 240, 180, 0.85)', 'text_color': '#cc9900'},
    {'id': 6, 'name': 'Документы', 'value': 'documents', 'color': 'rgba(220, 240, 220, 0.85)', 'text_color': '#009900'},
    {'id': 7, 'name': 'Отчеты', 'value': 'reports', 'color': 'rgba(240, 220, 220, 0.85)', 'text_color': '#cc3366'},
    {'id': 8, 'name': 'Рекомендации', 'value': 'recommendations', 'color': 'rgba(230, 220, 240, 0.85)', 'text_color': '#6600cc'},
]

NEWS_TARGET_AUDIENCES = [
    {'id': 1, 'name': 'Наставники', 'value': 'mentors', 'color': 'rgba(184, 212, 232, 0.85)'},
    {'id': 2, 'name': 'Администрация', 'value': 'administration', 'color': 'rgba(232, 212, 240, 0.85)'},
    {'id': 3, 'name': 'Молодые педагоги', 'value': 'young_teachers', 'color': 'rgba(245, 213, 184, 0.85)'},
    {'id': 4, 'name': 'Все педагоги', 'value': 'all_teachers', 'color': 'rgba(212, 232, 240, 0.85)'},
    {'id': 5, 'name': 'Классные руководители', 'value': 'class_leaders', 'color': 'rgba(220, 240, 220, 0.85)'},
    {'id': 6, 'name': 'Предметники', 'value': 'subject_teachers', 'color': 'rgba(240, 220, 220, 0.85)'},
]

NEWS_CONTENT_TYPES = [
    {'id': 1, 'name': 'Гранты и финансирование', 'value': 'grants', 'color': 'rgba(255, 220, 200, 0.85)'},
    {'id': 2, 'name': 'Наука и исследования', 'value': 'science', 'color': 'rgba(200, 230, 255, 0.85)'},
    {'id': 3, 'name': 'Повышение квалификации', 'value': 'training', 'color': 'rgba(220, 255, 220, 0.85)'},
    {'id': 4, 'name': 'Социальная поддержка', 'value': 'social_support', 'color': 'rgba(255, 220, 255, 0.85)'},
    {'id': 5, 'name': 'Творчество и проекты', 'value': 'creativity', 'color': 'rgba(255, 255, 200, 0.85)'},
    {'id': 6, 'name': 'Нормативные документы', 'value': 'regulations', 'color': 'rgba(230, 220, 240, 0.85)'},
]

# ========== МЕТОДИЧЕСКИЕ МАТЕРИАЛЫ ==========
MATERIAL_SUBJECTS = [
    {'id': 1, 'name': 'Биология', 'value': 'biology', 'bg_color': 'rgba(201, 228, 202, 0.85)', 'text_color': '#1e5128'},
    {'id': 2, 'name': 'География', 'value': 'geography', 'bg_color': 'rgba(184, 212, 232, 0.85)', 'text_color': '#0c4a6e'},
    {'id': 3, 'name': 'Дошкольное образование', 'value': 'preschool', 'bg_color': 'rgba(232, 212, 240, 0.85)', 'text_color': '#6b21a8'},
    {'id': 4, 'name': 'ИЗО и музыка', 'value': 'art_music', 'bg_color': 'rgba(245, 213, 184, 0.85)', 'text_color': '#c2410c'},
    {'id': 5, 'name': 'Иностранные языки', 'value': 'foreign_languages', 'bg_color': 'rgba(212, 232, 240, 0.85)', 'text_color': '#075985'},
    {'id': 6, 'name': 'Информатика и ИКТ', 'value': 'informatics', 'bg_color': 'rgba(184, 212, 232, 0.85)', 'text_color': '#0c4a6e'},
    {'id': 7, 'name': 'История и обществознание', 'value': 'history_social', 'bg_color': 'rgba(240, 232, 212, 0.85)', 'text_color': '#92400e'},
    {'id': 8, 'name': 'Математика', 'value': 'math', 'bg_color': 'rgba(201, 228, 202, 0.85)', 'text_color': '#1e5128'},
    {'id': 9, 'name': 'Начальные классы', 'value': 'elementary', 'bg_color': 'rgba(232, 212, 240, 0.85)', 'text_color': '#6b21a8'},
    {'id': 10, 'name': 'ОБЖ', 'value': 'safety', 'bg_color': 'rgba(245, 213, 184, 0.85)', 'text_color': '#c2410c'},
    {'id': 11, 'name': 'Русский язык и литература', 'value': 'russian', 'bg_color': 'rgba(212, 232, 240, 0.85)', 'text_color': '#075985'},
    {'id': 12, 'name': 'Технология', 'value': 'technology', 'bg_color': 'rgba(184, 212, 232, 0.85)', 'text_color': '#0c4a6e'},
    {'id': 13, 'name': 'Физика', 'value': 'physics', 'bg_color': 'rgba(240, 232, 212, 0.85)', 'text_color': '#92400e'},
    {'id': 14, 'name': 'Физическая культура', 'value': 'physical_education', 'bg_color': 'rgba(201, 228, 202, 0.85)', 'text_color': '#1e5128'},
    {'id': 15, 'name': 'Химия', 'value': 'chemistry', 'bg_color': 'rgba(232, 212, 240, 0.85)', 'text_color': '#6b21a8'},
]

MATERIAL_TYPES = [
    {'id': 1, 'name': 'Аудиоматериалы', 'value': 'audio', 'bg_color': 'rgba(201, 228, 202, 0.85)', 'text_color': '#1e5128'},
    {'id': 2, 'name': 'Видеоуроки', 'value': 'video', 'bg_color': 'rgba(184, 212, 232, 0.85)', 'text_color': '#0c4a6e'},
    {'id': 3, 'name': 'Дидактические материалы', 'value': 'didactic', 'bg_color': 'rgba(232, 212, 240, 0.85)', 'text_color': '#6b21a8'},
    {'id': 4, 'name': 'Интерактивные задания', 'value': 'interactive', 'bg_color': 'rgba(245, 213, 184, 0.85)', 'text_color': '#c2410c'},
    {'id': 5, 'name': 'Конспекты уроков', 'value': 'lesson_plans', 'bg_color': 'rgba(212, 232, 240, 0.85)', 'text_color': '#075985'},
    {'id': 6, 'name': 'Лабораторные работы', 'value': 'lab_works', 'bg_color': 'rgba(184, 212, 232, 0.85)', 'text_color': '#0c4a6e'},
    {'id': 7, 'name': 'Практикумы', 'value': 'practicums', 'bg_color': 'rgba(240, 232, 212, 0.85)', 'text_color': '#92400e'},
    {'id': 8, 'name': 'Презентации', 'value': 'presentations', 'bg_color': 'rgba(201, 228, 202, 0.85)', 'text_color': '#1e5128'},
    {'id': 9, 'name': 'Раздаточные материалы', 'value': 'handouts', 'bg_color': 'rgba(232, 212, 240, 0.85)', 'text_color': '#6b21a8'},
    {'id': 10, 'name': 'Сценарии уроков', 'value': 'lesson_scenarios', 'bg_color': 'rgba(245, 213, 184, 0.85)', 'text_color': '#c2410c'},
    {'id': 11, 'name': 'Тесты и контрольные работы', 'value': 'tests', 'bg_color': 'rgba(212, 232, 240, 0.85)', 'text_color': '#075985'},
    {'id': 12, 'name': 'Творческие проекты', 'value': 'creative_projects', 'bg_color': 'rgba(184, 212, 232, 0.85)', 'text_color': '#0c4a6e'},
]

MATERIAL_DIFFICULTY = [
    {'id': 1, 'name': 'Базовый уровень', 'value': 'basic'},
    {'id': 2, 'name': 'Задания для одаренных детей', 'value': 'gifted'},
    {'id': 3, 'name': 'Инклюзивное образование', 'value': 'inclusive'},
    {'id': 4, 'name': 'Коррекционные задания', 'value': 'correctional'},
    {'id': 5, 'name': 'Продвинутый уровень', 'value': 'advanced'},
    {'id': 6, 'name': 'Углубленное изучение', 'value': 'deep'},
]

MATERIAL_GRADES = [
    {'id': 1, 'name': '1-4 классы', 'value': '1-4'},
    {'id': 2, 'name': '5-6 классы', 'value': '5-6'},
    {'id': 3, 'name': '7-9 классы', 'value': '7-9'},
    {'id': 4, 'name': '10-11 классы', 'value': '10-11'},
    {'id': 5, 'name': 'Дошкольное образование', 'value': 'preschool'},
    {'id': 6, 'name': 'Среднее профессиональное образование', 'value': 'vocational'},
]

MATERIAL_FORMATS = [
    {'id': 1, 'name': 'Групповая работа', 'value': 'group'},
    {'id': 2, 'name': 'Дистанционное обучение', 'value': 'distance'},
    {'id': 3, 'name': 'Индивидуальная работа', 'value': 'individual'},
    {'id': 4, 'name': 'Парная работа', 'value': 'pair'},
    {'id': 5, 'name': 'Проектная деятельность', 'value': 'project'},
    {'id': 6, 'name': 'Смешанное обучение', 'value': 'blended'},
    {'id': 7, 'name': 'Фронтальная работа', 'value': 'frontal'},
]

MATERIAL_ASSESSMENT = [
    {'id': 1, 'name': 'С балльной системой', 'value': 'point'},
    {'id': 2, 'name': 'С взаимопроверкой', 'value': 'peer'},
    {'id': 3, 'name': 'С критериальным оцениванием', 'value': 'criteria'},
    {'id': 4, 'name': 'С самооценкой', 'value': 'self'},
    {'id': 5, 'name': 'С системой зачет/незачет', 'value': 'pass_fail'},
]

MATERIAL_ADDITIONAL = [
    {'id': 1, 'name': 'Авторские методики', 'value': 'author_methods'},
    {'id': 2, 'name': 'Внеурочная деятельность', 'value': 'extracurricular'},
    {'id': 3, 'name': 'К праздничным датам', 'value': 'holiday'},
    {'id': 4, 'name': 'Краеведческие материалы', 'value': 'local_history'},
    {'id': 5, 'name': 'Материалы для замены уроков', 'value': 'substitute'},
    {'id': 6, 'name': 'Подготовка к олимпиадам', 'value': 'olympiad_prep'},
    {'id': 7, 'name': 'Подготовка к экзаменам', 'value': 'exam_prep'},
    {'id': 8, 'name': 'Профориентационные уроки', 'value': 'career_guidance'},
    {'id': 9, 'name': 'Сезонные материалы', 'value': 'seasonal'},
    {'id': 10, 'name': 'Экспериментальные разработки', 'value': 'experimental'},
]

# ========== НОРМАТИВНЫЕ ДОКУМЕНТЫ ==========
DOCUMENT_CATEGORIES = [
    {'id': 1, 'name': 'ФГОС', 'value': 'fgos', 'bg_color': 'rgba(184, 212, 232, 0.85)', 'text_color': '#0c4a6e'},
    {'id': 2, 'name': 'Федеральные законы', 'value': 'federal_laws', 'bg_color': 'rgba(201, 228, 202, 0.85)', 'text_color': '#1e5128'},
    {'id': 3, 'name': 'Приказы', 'value': 'orders', 'bg_color': 'rgba(232, 212, 240, 0.85)', 'text_color': '#6b21a8'},
    {'id': 4, 'name': 'Методические рекомендации', 'value': 'method_recommendations', 'bg_color': 'rgba(245, 213, 184, 0.85)', 'text_color': '#c2410c'},
    {'id': 5, 'name': 'Профстандарты', 'value': 'prof_standards', 'bg_color': 'rgba(212, 232, 240, 0.85)', 'text_color': '#075985'},
    {'id': 6, 'name': 'Локальные акты', 'value': 'local_acts', 'bg_color': 'rgba(255, 228, 196, 0.85)', 'text_color': '#92400e'},
    {'id': 7, 'name': 'Санитарные нормы', 'value': 'sanitary_norms', 'bg_color': 'rgba(220, 220, 235, 0.85)', 'text_color': '#4c1d95'},
]

DOCUMENT_LEVELS = [
    {'id': 1, 'name': 'Федеральный', 'value': 'federal'},
    {'id': 2, 'name': 'Региональный', 'value': 'regional'},
    {'id': 3, 'name': 'Локальный', 'value': 'local'},
]

DOCUMENT_YEARS = [
    {'id': 1, 'name': '2024', 'value': '2024'},
    {'id': 2, 'name': '2023', 'value': '2023'},
    {'id': 3, 'name': '2022', 'value': '2022'},
    {'id': 4, 'name': '2021', 'value': '2021'},
    {'id': 5, 'name': '2020 и ранее', 'value': '2020_earlier'},
]

# ========== ОПРОСЫ ==========
SURVEY_CATEGORIES = [
    {'id': 1, 'name': 'Адаптация молодых специалистов', 'value': 'adaptation'},
    {'id': 2, 'name': 'Удовлетворённость мероприятиями', 'value': 'satisfaction'},
    {'id': 3, 'name': 'Оценка методических материалов', 'value': 'materials_evaluation'},
    {'id': 4, 'name': 'Выявление потребностей', 'value': 'needs_identification'},
    {'id': 5, 'name': 'Обратная связь', 'value': 'feedback'},
]

SURVEY_STATUSES = [
    {'id': 1, 'name': 'Черновик', 'value': 'draft'},
    {'id': 2, 'name': 'Активный', 'value': 'active'},
    {'id': 3, 'name': 'Завершённый', 'value': 'completed'},
    {'id': 4, 'name': 'Архивный', 'value': 'archived'},
]

QUESTION_TYPES = [
    {'id': 1, 'name': 'Открытый вопрос', 'value': 'text'},
    {'id': 2, 'name': 'Одиночный выбор', 'value': 'single'},
    {'id': 3, 'name': 'Множественный выбор', 'value': 'multiple'},
]