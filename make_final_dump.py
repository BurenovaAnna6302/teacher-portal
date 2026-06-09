import os
import json
import django
from django.core import serializers
from django.apps import apps

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Только ваши приложения (без auth, contenttypes, admin, sessions)
my_apps = [
    'main', 'about', 'news', 'events', 'materials', 'documents',
    'surveys', 'members', 'teachers', 'account', 'admin_panel', 'success_practices'
]

all_objects = []
for app_name in my_apps:
    try:
        app_config = apps.get_app_config(app_name)
    except LookupError:
        print(f"Приложение {app_name} не найдено, пропускаем")
        continue
    for model in app_config.get_models():
        qs = model.objects.all()
        if qs.exists():
            all_objects.extend(qs)

# Сериализация с отключённым экранированием не-ASCII символов
data = serializers.serialize('json', all_objects, indent=2, ensure_ascii=False)

# Исправляем пути к фото (подставляем правильные папки)
data = data.replace('news/photos/', 'news/images/news_photos/')
data = data.replace('events/photos/', 'events/images/event_photos/')
# Если есть другие приложения с подобными путями, добавьте аналогичные строки

with open('final_dump.json', 'w', encoding='utf-8') as f:
    f.write(data)

print(f"✅ Финальный дамп создан: final_dump.json")
print(f"   Объектов: {len(all_objects)}")