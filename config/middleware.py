# config/middleware.py
class UserTypeMiddleware:
    """
    Синхронизирует тип пользователя и гарантирует,
    что админ имеет приоритет над педагогом
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Получаем ответ
        response = self.get_response(request)

        # Если админ авторизован, но есть остатки данных педагога - чистим
        if request.session.get('admin_authenticated') and request.session.get('is_admin'):
            # Удаляем любые остатки данных педагога
            teacher_keys = ['user_id', 'user_authenticated', 'user_email',
                            'user_data', 'profile_data', 'teacher_id']
            for key in teacher_keys:
                if key in request.session:
                    del request.session[key]

            # Гарантируем, что is_admin = True
            if not request.session.get('is_admin'):
                request.session['is_admin'] = True

            request.session['user_type'] = 'admin'

        # Если нет админа, но есть педагог
        elif request.session.get('user_id') and not request.session.get('admin_authenticated'):
            request.session['user_type'] = 'teacher'

        return response