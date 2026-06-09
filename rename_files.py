import json
import os
import shutil

with open('my_clean_dump.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Словарь для переименования: (путь назначения) -> исходное имя
# Сначала скопируем все файлы в нужные папки с нужными именами

news_src = 'news/static/news/images/news_photos'
news_dst = 'news/static/news/photos'
os.makedirs(news_dst, exist_ok=True)

events_src = 'events/static/events/images/event_photos'
events_dst = 'events/static/events/photos'
os.makedirs(events_dst, exist_ok=True)

# Обрабатываем новости
for item in data:
    if item.get('model') == 'news.newsphoto':
        photo_path = item['fields']['photo']
        # photo_path вида "news/photos/news_1_1_1_1_Uv6fBfh.jpg"
        filename = os.path.basename(photo_path)
        # Извлекаем номер новости и номер фото (пример: news_1_1_... -> 1_1)
        parts = filename.split('_')
        if len(parts) >= 3:
            news_num = parts[1]
            photo_num = parts[2]
            # Ищем исходный файл: например, {news_num}_{photo_num}.jpg
            src_file = os.path.join(news_src, f'{news_num}_{photo_num}.jpg')
            dst_file = os.path.join(news_dst, filename)
            if os.path.exists(src_file):
                shutil.copy2(src_file, dst_file)
                print(f'Скопирован {src_file} -> {dst_file}')
            else:
                print(f'Не найден {src_file}')

# Аналогично для событий
for item in data:
    if item.get('model') == 'events.eventphoto':
        photo_path = item['fields']['photo']
        filename = os.path.basename(photo_path)
        parts = filename.split('_')
        if len(parts) >= 3:
            event_num = parts[1]
            photo_num = parts[2]
            src_file = os.path.join(events_src, f'event_{event_num}_{photo_num}.jpg')
            dst_file = os.path.join(events_dst, filename)
            if os.path.exists(src_file):
                shutil.copy2(src_file, dst_file)
                print(f'Скопирован {src_file} -> {dst_file}')
            else:
                print(f'Не найден {src_file}')