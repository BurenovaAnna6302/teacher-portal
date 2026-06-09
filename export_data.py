import os
import json
from django.core import serializers
from django.apps import apps

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

# Список ваших приложений
apps_list = [
    'main', 'about', 'news', 'events', 'materials', 'documents',
    'surveys', 'members', 'teachers', 'account', 'admin_panel', 'success_practices'
]

all_objects = []
for app_name in apps_list:
    try:
        app_config = apps.get_app_config(app_name)
    except LookupError:
        print(f"Приложение {app_name} не найдено, пропускаем")
        continue
    for model in app_config.get_models():
        qs = model.objects.all()
        if qs.exists():
            all_objects.extend(qs)

# Сериализуем в JSON с отключённым экранированием не-ASCII символов
data = serializers.serialize('json', all_objects, indent=2, ensure_ascii=False)

# Сохраняем в файл с явной кодировкой UTF-8
with open('my_apps_data_final.json', 'w', encoding='utf-8') as f:
    f.write(data)

print("✅ Экспорт завершён: my_apps_data_final.json")