
import os
import django
from django.core import serializers
from django.apps import apps

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Исключаем системные приложения, которые могут вызвать конфликты
exclude_apps = ['auth', 'contenttypes', 'admin', 'sessions']
all_objects = []

for app_config in apps.get_app_configs():
    if app_config.name in exclude_apps:
        continue
    for model in app_config.get_models():
        qs = model.objects.all()
        if qs.exists():
            all_objects.extend(qs)

data = serializers.serialize('json', all_objects, indent=2, ensure_ascii=False)

with open('full_dump_fixed.json', 'w', encoding='utf-8') as f:
    f.write(data)

print("✅ Дамп создан: full_dump_fixed.json")