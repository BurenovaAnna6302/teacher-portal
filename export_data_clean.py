import os
import django
from django.core import serializers

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Список ваших приложений (только те, данные которых нужно экспортировать)
my_apps = [
    'main', 'about', 'news', 'events', 'materials', 'documents',
    'surveys', 'members', 'teachers', 'account', 'admin_panel', 'success_practices'
]

all_objects = []
for app in my_apps:
    try:
        app_config = django.apps.apps.get_app_config(app)
    except LookupError:
        print(f"Приложение {app} не найдено, пропускаем")
        continue
    for model in app_config.get_models():
        qs = model.objects.all()
        if qs.exists():
            all_objects.extend(qs)

# Сериализуем только свои модели
data = serializers.serialize('json', all_objects, indent=2, ensure_ascii=False)

with open('my_clean_data.json', 'w', encoding='utf-8') as f:
    f.write(data)

print(f"✅ Экспортировано {len(all_objects)} объектов в my_clean_data.json")