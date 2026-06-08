from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password, check_password
import json
import re
from .models import Teacher

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.urls import reverse
from django.contrib.auth.hashers import make_password, check_password


# Список всех предметных специализаций
ALL_SPECIALIZATIONS = [
    "Математика", "Русский язык и литература", "Английский язык",
    "Немецкий язык", "Французский язык", "История", "Обществознание",
    "География", "Биология", "Физика", "Химия", "Информатика",
    "Физическая культура", "Технология", "Музыка", "ИЗО", "МХК",
    "ОБЖ", "Начальные классы", "Дошкольное образование", "Логопедия",
    "Психология", "Социальная педагогика", "Другое"
]




def login_view(request):
    """Страница входа с поддержкой AJAX (без перезагрузки)"""
    if request.session.get('user_authenticated'):
        return redirect('account:profile')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        errors = {}

        # Валидация email
        if not email:
            errors['email'] = 'Введите email'
        elif '@' not in email or '.' not in email:
            errors['email'] = 'Введите корректный email адрес'
        elif len(email) > 30:
            errors['email'] = 'Email не должен превышать 30 символов'

        # Валидация пароля
        if not password:
            errors['password'] = 'Введите пароль'
        elif len(password) < 6:
            errors['password'] = 'Пароль должен содержать минимум 6 символов'
        elif len(password) > 30:
            errors['password'] = 'Пароль не должен превышать 30 символов'

        # Если валидация прошла, проверяем в БД
        if not errors:
            try:
                teacher = Teacher.objects.get(email=email)
                if check_password(password, teacher.password):
                    # Устанавливаем сессию
                    request.session['user_email'] = email
                    request.session['user_authenticated'] = True
                    request.session['user_id'] = teacher.id

                    user_session_data = {
                        'id': teacher.id,
                        'email': email,
                        'first_name': teacher.first_name,
                        'last_name': teacher.last_name,
                        'middle_name': teacher.middle_name or '',
                        'is_authenticated': True,
                    }
                    request.session['user_data'] = user_session_data

                    profile_data = {
                        'email': email,
                        'first_name': teacher.first_name,
                        'last_name': teacher.last_name,
                        'middle_name': teacher.middle_name or '',
                        'educational_institution': teacher.educational_institution or '',
                        'experience': teacher.experience or '',
                        'category': teacher.category or '',
                        'specialization': teacher.specialization or '',
                        'specializations': teacher.specializations or '',
                        'photo_url': teacher.photo.url if teacher.photo else None,
                    }
                    request.session['profile_data'] = profile_data
                    request.session.save()

                    # AJAX-запрос
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({'success': True, 'redirect_url': reverse('account:profile')})
                    return redirect('account:profile')
                else:
                    errors['password'] = 'Неверный пароль'
            except Teacher.DoesNotExist:
                errors['email'] = 'Пользователь с таким email не найден'

        # AJAX-запрос с ошибками
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'errors': errors}, status=400)

        # Обычный POST-запрос (рендер с ошибками)
        return render(request, 'auth/login.html', {
            'email_value': email,
            'error_email': errors.get('email'),
            'error_password': errors.get('password'),
        })

    # GET-запрос
    return render(request, 'auth/login.html')


def register_view(request):
    """Страница регистрации"""
    if request.method == 'POST':
        # Получаем данные формы
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        middle_name = request.POST.get('middle_name', '').strip()
        educational_institution = request.POST.get('educational_institution', '').strip()
        experience = request.POST.get('experience', '').strip()
        category = request.POST.get('category', '').strip()
        specializations = request.POST.getlist('specializations', [])

        # Удаляем дубликаты в специализациях
        if specializations:
            specializations = list(dict.fromkeys(specializations))

        # Валидация
        errors = {}
        name_pattern = re.compile(r'^[А-Яа-яЁё\s\-]+$')

        # Email
        if not email:
            errors['email'] = 'Пожалуйста, введите email'
        elif '@' not in email or '.' not in email:
            errors['email'] = 'Введите корректный email адрес'
        elif len(email) > 30:
            errors['email'] = 'Email не должен превышать 30 символов'
        elif Teacher.objects.filter(email=email).exists():
            errors['email'] = 'Пользователь с таким email уже существует'

        # Пароль
        if not password:
            errors['password'] = 'Пожалуйста, введите пароль'
        elif len(password) < 6:
            errors['password'] = 'Пароль должен содержать минимум 6 символов'
        elif len(password) > 30:
            errors['password'] = 'Пароль не должен превышать 30 символов'
        elif password != confirm_password:
            errors['confirm_password'] = 'Пароли не совпадают'

        # Имя и фамилия
        if not first_name:
            errors['first_name'] = 'Пожалуйста, введите имя'
        elif len(first_name) > 30:
            errors['first_name'] = 'Имя не должно превышать 30 символов'
        elif not name_pattern.match(first_name):
            errors['first_name'] = 'Только русские буквы, дефисы и пробелы'

        if not last_name:
            errors['last_name'] = 'Пожалуйста, введите фамилию'
        elif len(last_name) > 30:
            errors['last_name'] = 'Фамилия не должна превышать 30 символов'
        elif not name_pattern.match(last_name):
            errors['last_name'] = 'Только русские буквы, дефисы и пробелы'

        if middle_name and (len(middle_name) > 30 or not name_pattern.match(middle_name)):
            errors['middle_name'] = 'Отчество должно содержать только русские буквы'

        # Образовательное учреждение (необязательное)
        if educational_institution and len(educational_institution) > 200:
            errors['educational_institution'] = 'Название учреждения не должно превышать 200 символов'

        # Стаж (необязательный)
        if experience:
            try:
                exp_int = int(experience)
                if exp_int < 0 or exp_int > 100:
                    errors['experience'] = 'Стаж должен быть от 0 до 100 лет'
            except ValueError:
                errors['experience'] = 'Стаж должен быть числом'

        # Специализации - необязательное поле
        if specializations:
            valid_specializations = [s for s in specializations if s in ALL_SPECIALIZATIONS]
            if len(valid_specializations) != len(specializations):
                errors['specializations'] = 'Некорректные значения специализаций'

        if errors:
            return render(request, 'auth/register.html', {
                'errors': errors,
                'form_data': {
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name,
                    'middle_name': middle_name,
                    'educational_institution': educational_institution,
                    'experience': experience,
                    'category': category,
                    'specializations': specializations,
                },
                'all_specializations': ALL_SPECIALIZATIONS,
            })

        # Создаем пользователя
        teacher = Teacher.objects.create(
            email=email,
            password=make_password(password),
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name if middle_name else None,
            educational_institution=educational_institution if educational_institution else None,
            experience=int(experience) if experience else None,
            category=category if category else None,
            specializations=','.join(specializations) if specializations else None,
        )

        # Создаем сессию
        request.session['user_email'] = email
        request.session['user_authenticated'] = True
        request.session['user_id'] = teacher.id

        user_session_data = {
            'id': teacher.id,
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'middle_name': middle_name,
            'is_authenticated': True,
        }

        request.session['user_data'] = user_session_data

        profile_data = {
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'middle_name': middle_name,
            'educational_institution': educational_institution,
            'experience': experience,
            'category': category,
            'specializations': ','.join(specializations) if specializations else '',
            'photo_url': None,
        }

        request.session['profile_data'] = profile_data
        request.session.save()

        return redirect('account:profile')

    # GET запрос
    return render(request, 'auth/register.html', {
        'all_specializations': ALL_SPECIALIZATIONS,
    })


def logout_view(request):
    """Выход из системы"""
    request.session.flush()
    return redirect('main:index')


def check_auth(request):
    """Проверка авторизации (для AJAX)"""
    if request.session.get('user_authenticated'):
        return JsonResponse({
            'authenticated': True,
            'email': request.session.get('user_email'),
            'first_name': request.session.get('user_data', {}).get('first_name', '')
        })
    return JsonResponse({'authenticated': False})