import json
import re

# Открываем ваш дамп (тот, который вы загружали на сервер)
with open('full_dump_fixed.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Проходим по всем объектам
for obj in data:
    # Исправляем пути для фото новостей
    if obj.get('model') == 'news.newsphoto':
        old_path = obj['fields']['photo']
        # old_path = "news/photos/news_1_1_1_1_Uv6fBfh.jpg"
        # Извлекаем news_pk и номер фото
        match = re.search(r'news_(\d+)_(\d+)_\d+_\d+_\w+\.jpg', old_path)
        if match:
            news_pk = match.group(1)
            photo_num = match.group(2)
            new_name = f'{news_pk}_{photo_num}.jpg'
            new_path = f'news/images/news_photos/{new_name}'
            obj['fields']['photo'] = new_path
            print(f'Исправлено: {old_path} -> {new_path}')

    # Исправляем пути для фото событий
    if obj.get('model') == 'events.eventphoto':
        old_path = obj['fields']['photo']
        # old_path = "events/photos/event_1_1_1_1_BPBLYFA.jpg"
        match = re.search(r'event_(\d+)_(\d+)_\d+_\d+_\w+\.jpg', old_path)
        if match:
            event_pk = match.group(1)
            photo_num = match.group(2)
            new_name = f'event_{event_pk}_{photo_num}.jpg'  # или просто f'event_{event_pk}_{photo_num}.jpg'?
            # У Анны в папке event_photos файлы названы event_1_1.jpg, event_1_2.jpg и т.д.
            new_path = f'events/images/event_photos/{new_name}'
            obj['fields']['photo'] = new_path
            print(f'Исправлено: {old_path} -> {new_path}')

# Сохраняем исправленный дамп
with open('fixed_dump_short.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print('Готово! Исправленный дамп: fixed_dump_short.json')