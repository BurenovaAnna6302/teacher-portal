# config/middleware.py
class AdminSessionCleanupMiddleware:
    """
    Скрывает админ-интерфейс на публичных страницах
    И очищает сообщения админки
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Публичные страницы
        public_paths = [
            '/practices/', '/news/', '/events/', '/about/',
            '/materials/', '/documents/', '/surveys/', '/'
        ]

        is_public = any(request.path.startswith(path) for path in public_paths)
        is_admin_auth = request.session.get('admin_authenticated')

        if is_public and is_admin_auth:
            # Скрываем админ-интерфейс
            request.session['is_admin'] = False

            # ОЧИЩАЕМ СООБЩЕНИЯ на публичных страницах
            if '_messages' in request.session:
                # Сохраняем копию сообщений для админки
                if not hasattr(request, '_admin_messages_backup'):
                    request._admin_messages_backup = request.session.get('_messages', [])
                # Очищаем сообщения для публичной страницы
                del request.session['_messages']

        # Если вернулись в админку - восстанавливаем сообщения?
        elif request.path.startswith('/dashboard/') and is_admin_auth:
            request.session['is_admin'] = True
            # Восстанавливаем сообщения (опционально)
            if hasattr(request, '_admin_messages_backup'):
                request.session['_messages'] = request._admin_messages_backup

        return response