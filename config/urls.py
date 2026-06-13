from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse

# Простая функция для верификации Яндекса (отдаём просто текст)
from django.http import HttpResponse


def yandex_verification(request):
    """Файл верификации для Яндекс.Вебмастера"""
    html_content = """<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    </head>
     <body>Verification: cb2afd2e28a99dbc</body>

</html>"""
    return HttpResponse(html_content, content_type='text/html; charset=utf-8')


urlpatterns = [
    # Файл верификации Яндекса
    path('yandex_cb2afd2e28a99dbc.html', yandex_verification),

    # Все основные маршруты (как было изначально)
    path('admin/', admin.site.urls),
    path('dashboard/', include('admin_panel.urls')),
    path('', include('main.urls')),
    path('auth/', include(('teachers.urls', 'teachers'), namespace='auth')),
    path('account/', include('account.urls')),
    path('about/', include('about.urls')),
    path('news/', include('news.urls')),
    path('events/', include('events.urls')),
    path('materials/', include('materials.urls')),
    path('documents/', include('documents.urls')),
    path('surveys/', include('surveys.urls')),
    path('members/', include('members.urls')),
    path('practices/', include('success_practices.urls')),
]

# Медиа и статика в режиме разработки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)