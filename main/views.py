import json
import requests
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone
from news.models import News
from events.models import Event

TELEGRAM_BOT_TOKEN = '8449676799:AAHa56OrRCJHVNg45zkD1omg_pTmtJzWNXA'
TELEGRAM_CHAT_ID = '-1003712543639'


def index_view(request):
    """Главная страница с последними новостями и мероприятиями"""

    # Получаем последние 3 новости
    latest_news = News.objects.filter(is_published=True).select_related(
        'info_status', 'target_audience', 'content_type'
    ).prefetch_related('photos').order_by('-publication_date')[:3]

    # Получаем ближайшие 3 мероприятия (будущие)
    from datetime import date
    latest_events = Event.objects.filter(
        is_published=True,
        date__gte=date.today()
    ).select_related(
        'target_audience', 'format', 'activity_type', 'subject'
    ).prefetch_related('photos').order_by('date', 'title')[:3]

    context = {
        'latest_news': latest_news,
        'latest_events': latest_events,
    }
    return render(request, 'main/index.html', context)


@csrf_exempt
@require_POST
def contact_view(request):
    print(f"📞 Получен POST запрос на форму")

    try:
        data = json.loads(request.body.decode('utf-8'))
        print(f"📦 Данные формы: {data}")

        # Валидация обязательных полей
        required_fields = ['name', 'email', 'subject', 'message']
        for field in required_fields:
            if not data.get(field, '').strip():
                return JsonResponse({
                    'success': False,
                    'message': f'Пожалуйста, заполните поле: {field}'
                }, status=400)

        # Валидация email
        email = data.get('email', '').strip()
        if '@' not in email or '.' not in email:
            return JsonResponse({
                'success': False,
                'message': 'Пожалуйста, введите корректный email адрес'
            }, status=400)

        # Отправляем в Telegram
        success = send_to_telegram(data)

        if success:
            return JsonResponse({
                'success': True,
                'message': '✅ Ваше сообщение отправлено! Мы свяжемся с вами в ближайшее время.'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': '❌ Ошибка при отправке сообщения. Пожалуйста, попробуйте позже или свяжитесь с нами другим способом.'
            })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Неверный формат данных'
        }, status=400)
    except Exception as e:
        print(f"❌ Ошибка сервера: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'message': 'Внутренняя ошибка сервера'
        }, status=500)


def send_to_telegram(data):
    """Отправка сообщения в Telegram с красивым форматированием"""
    try:
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        subject = data.get('subject', '').strip()
        message = data.get('message', '').strip()

        text = "\n\n\n*НОВАЯ ЗАЯВКА С САЙТА*\n"
        text += "=" * 28 + "\n\n"

        text += f"*ИМЯ ОТПРАВИТЕЛЯ:* \n{name}\n\n"
        text += f"*ПОЧТА ДЛЯ ОБРАТНОЙ СВЯЗИ:* `{email}`\n\n"
        text += f"*ТЕМА ОБРАЩЕНИЯ:* \n{subject}\n"
        text += "\n*СООБЩЕНИЕ:*\n"
        text += f"{message}\n"
        text += "\n**Время отправки:**\n"
        text += f"{timezone.now().strftime('%d.%m.%Y %H:%M:%S')}\n"
        text += "\n" + "=" * 28

        url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': text,
            'parse_mode': 'Markdown',
            'disable_web_page_preview': True
        }

        print(f"📤 Отправляю в Telegram...")
        response = requests.post(url, data=payload, timeout=10)

        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                print("✅ Сообщение отправлено в Telegram!")
                return True
            else:
                print(f"❌ Telegram API error: {result}")
                return False
        else:
            print(f"❌ HTTP error: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False