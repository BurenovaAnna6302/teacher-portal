from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.views.generic import TemplateView


# ===== ФУНКЦИИ ДЛЯ СЕРВИСНЫХ ФАЙЛОВ =====

def yandex_verification(request):
    """Файл верификации для Яндекс.Вебмастера"""
    html_content = '<html><head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8"></head><body>cb2afd2e28a99dbc</body></html>'
    return HttpResponse(html_content, content_type='text/html')


def google_verification(request):
    """Файл верификации для Google Search Console (если понадобится)"""
    # Замените 'ваш-google-код' на реальный код от Google
    return HttpResponse('google-site-verification: ваш-google-код', content_type='text/plain')


# ===== МАРШРУТЫ =====

urlpatterns = [
    # ===== СЕРВИСНЫЕ ФАЙЛЫ (должны быть в самом начале!) =====
    path('yandex_cb2afd2e28a99dbc.html', yandex_verification, name='yandex_verification'),
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain'), name='robots_txt'),
    path('sitemap.xml', TemplateView.as_view(template_name='sitemap.xml', content_type='application/xml'),
         name='sitemap_xml'),

    # ===== АДМИНКА =====
    path('admin/', admin.site.urls),
    path('dashboard/', include('admin_panel.urls')),

    # ===== ОСНОВНЫЕ СТРАНИЦЫ =====
    path('', include('main.urls')),
    path('contact/', include('contact.urls', namespace='contact')),

    # ===== АВТОРИЗАЦИЯ И ЛИЧНЫЙ КАБИНЕТ =====
    path('auth/', include(('teachers.urls', 'teachers'), namespace='auth')),
    path('account/', include('account.urls', namespace='account')),

    # ===== РАЗДЕЛЫ САЙТА =====
    path('about/', include('about.urls', namespace='about')),
    path('news/', include('news.urls', namespace='news')),
    path('events/', include('events.urls', namespace='events')),
    path('materials/', include('materials.urls', namespace='materials')),
    path('documents/', include('documents.urls', namespace='documents')),
    path('surveys/', include('surveys.urls', namespace='surveys')),
    path('members/', include('members.urls', namespace='members')),
    path('practices/', include('success_practices.urls', namespace='success_practices')),
]

# ===== МЕДИА-ФАЙЛЫ (только в режиме разработки) =====
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)