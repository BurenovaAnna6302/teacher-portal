import os
import json
import django
from django.core import serializers

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Только ваши приложения (список из INSTALLED_APPS)
my_apps = [
    'main', 'about', 'news', 'events', 'materials', 'documents',
    'surveys', 'members', 'teachers', 'account', 'admin_panel', 'success_practices'
]

all_objects = []
for app_name in my_apps:
    app_config = django.apps.apps.get_app_config(app_name)
    for model in app_config.get_models():
        qs = model.objects.all()
        if qs.exists():
            all_objects.extend(qs)

data = serializers.serialize('json', all_objects, indent=2, ensure_ascii=False)

with open('my_clean_dump.json', 'w', encoding='utf-8') as f:
    f.write(data)

print(f"✅ Создан чистый дамп my_clean_dump.json, объектов: {len(all_objects)}")