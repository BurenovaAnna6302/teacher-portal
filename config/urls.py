from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard/', include('admin_panel.urls')),
    path('', include('main.urls')),
    # ВАЖНО: добавьте namespace='auth' для teachers
    path('auth/', include(('teachers.urls', 'teachers'), namespace='auth')),
    path('account/', include('account.urls')),
    path('about/', include('about.urls')),
    path('news/', include('news.urls')),
    path('events/', include('events.urls')),
    path('materials/', include('materials.urls')),
    path('documents/', include('documents.urls')),
    path('surveys/', include('surveys.urls')),
    path('members/', include('members.urls')),
    path('practices/', include('success_practices.urls')),  # ← ДОБАВЛЕНО
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)