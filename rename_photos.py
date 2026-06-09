import os
import json
import shutil

# Пути
BASE = os.path.dirname(__file__)
DUMP = os.path.join(BASE, 'my_clean_dump.json')  # если файл называется иначе, исправьте

# Исходные папки с короткими именами
NEWS_SRC = os.path.join(BASE, 'news', 'static', 'news', 'images', 'news_photos')
EVENTS_SRC = os.path.join(BASE, 'events', 'static', 'events', 'images', 'event_photos')

# Папки назначения (будут созданы автоматически)
NEWS_DST = os.path.join(BASE, 'news', 'static', 'news', 'photos')
EVENTS_DST = os.path.join(BASE, 'events', 'static', 'events', 'photos')

os.makedirs(NEWS_DST, exist_ok=True)
os.makedirs(EVENTS_DST, exist_ok=True)

# Читаем дамп
with open(DUMP, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Копируем и переименовываем новости
for item in data:
    if item.get('model') == 'news.newsphoto':
        target_name = os.path.basename(item['fields']['photo'])   # news_1_1_1_1_Uv6fBfh.jpg
        # Извлекаем номер новости и номер фото
        parts = target_name.split('_')
        if len(parts) >= 3:
            news_num = parts[1]
            photo_num = parts[2]
            src_file = os.path.join(NEWS_SRC, f'{news_num}_{photo_num}.jpg')
            dst_file = os.path.join(NEWS_DST, target_name)
            if os.path.exists(src_file):
                shutil.copy2(src_file, dst_file)
                print(f'OK: {src_file} -> {dst_file}')
            else:
                print(f'!!! Не найден: {src_file}')

# Копируем и переименовываем события
for item in data:
    if item.get('model') == 'events.eventphoto':
        target_name = os.path.basename(item['fields']['photo'])   # event_1_1_1_1_BPBLYFA.jpg
        parts = target_name.split('_')
        if len(parts) >= 3:
            event_num = parts[1]
            photo_num = parts[2]
            src_file = os.path.join(EVENTS_SRC, f'event_{event_num}_{photo_num}.jpg')
            dst_file = os.path.join(EVENTS_DST, target_name)
            if os.path.exists(src_file):
                shutil.copy2(src_file, dst_file)
                print(f'OK: {src_file} -> {dst_file}')
            else:
                print(f'!!! Не найден: {src_file}')

print('ГОТОВО! Теперь закоммитьте папки news/static/news/photos/ и events/static/events/photos/')