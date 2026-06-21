import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from news.models import News
from events.models import Event


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

        # Отправляем на EMAIL
        success = send_to_email(data)

        if success:
            return JsonResponse({
                'success': True,
                'message': '✅ Ваше сообщение отправлено! Мы свяжемся с вами в ближайшее время.'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': '❌ Ошибка при отправке сообщения. Пожалуйста, попробуйте позже или свяжитесь с нами другим способом.'
            }, status=500)

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


def send_to_email(data):
    """Отправка сообщения на email с красивым форматированием"""
    try:
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        subject = data.get('subject', '').strip()
        message = data.get('message', '').strip()

        # Формируем тему письма
        email_subject = f'Новая заявка с сайта: {subject}'

        # Формируем текст письма
        email_message = f"""НОВАЯ ЗАЯВКА С САЙТА
{'=' * 50}

ИМЯ ОТПРАВИТЕЛЯ:
{name}

ПОЧТА ДЛЯ ОБРАТНОЙ СВЯЗИ:
{email}

ТЕМА ОБРАЩЕНИЯ:
{subject}

СООБЩЕНИЕ:
{message}

{'=' * 50}
Время отправки: {timezone.now().strftime('%d.%m.%Y %H:%M:%S')}
"""

        print(f"📤 Отправляю email на {settings.EMAIL_RECEIVER}...")

        # Отправляем письмо
        send_mail(
            subject=email_subject,
            message=email_message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.EMAIL_RECEIVER],
            fail_silently=False,
        )

        print("✅ Сообщение отправлено на email!")
        return True

    except Exception as e:
        print(f"❌ Ошибка при отправке email: {e}")
        import traceback
        traceback.print_exc()
        return False