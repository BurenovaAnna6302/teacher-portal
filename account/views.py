from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import os
import re
from teachers.models import Teacher
from materials.models import Material
from .models import Favorite


# Список всех предметных специализаций
ALL_SPECIALIZATIONS = [
    "Математика", "Русский язык и литература", "Английский язык",
    "Немецкий язык", "Французский язык", "История", "Обществознание",
    "География", "Биология", "Физика", "Химия", "Информатика",
    "Физическая культура", "Технология", "Музыка", "ИЗО", "МХК",
    "ОБЖ", "Начальные классы", "Дошкольное образование", "Логопедия",
    "Психология", "Социальная педагогика", "Другое"
]


def profile(request):
    """Страница профиля"""
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('teachers:login')

    try:
        teacher = Teacher.objects.get(id=user_id)
    except Teacher.DoesNotExist:
        return redirect('teachers:login')

    if request.method == 'POST':
        try:
            # Обновляем данные
            teacher.email = request.POST.get('email', teacher.email)
            teacher.first_name = request.POST.get('first_name', teacher.first_name)
            teacher.last_name = request.POST.get('last_name', teacher.last_name)
            teacher.middle_name = request.POST.get('middle_name') or None
            teacher.educational_institution = request.POST.get('educational_institution') or None

            experience = request.POST.get('experience')
            if experience:
                try:
                    teacher.experience = int(experience)
                except:
                    teacher.experience = None
            else:
                teacher.experience = None

            # Получаем специализации из POST (множественный выбор)
            specializations = request.POST.getlist('specializations', [])
            if specializations:
                teacher.specializations = ','.join(specializations)
            else:
                teacher.specializations = None

            if 'photo' in request.FILES:
                if teacher.photo:
                    try:
                        if os.path.isfile(teacher.photo.path):
                            os.remove(teacher.photo.path)
                    except:
                        pass
                teacher.photo = request.FILES['photo']
            elif request.POST.get('remove_photo') == 'true':
                if teacher.photo:
                    try:
                        if os.path.isfile(teacher.photo.path):
                            os.remove(teacher.photo.path)
                    except:
                        pass
                    teacher.photo = None

            teacher.save()

            # Обновляем сессию
            user_data = {
                'id': teacher.id,
                'email': teacher.email,
                'first_name': teacher.first_name,
                'last_name': teacher.last_name,
                'middle_name': teacher.middle_name or '',
                'is_authenticated': True,
            }
            request.session['user_data'] = user_data

            profile_data = {
                'email': teacher.email,
                'first_name': teacher.first_name,
                'last_name': teacher.last_name,
                'middle_name': teacher.middle_name or '',
                'educational_institution': teacher.educational_institution or '',
                'experience': teacher.experience or '',
                'specializations': teacher.specializations or '',
                'photo_url': teacher.photo.url if teacher.photo else None,
            }
            request.session['profile_data'] = profile_data
            request.session.modified = True

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Профиль обновлен',
                    'photo_url': teacher.photo.url if teacher.photo else None,
                })

            return redirect('account:profile')

        except Exception as e:
            print(f"Ошибка: {e}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': str(e)}, status=400)

    favorites_count = Favorite.objects.filter(teacher=teacher).count()

    context = {
        'user': teacher,
        'profile_data': {
            'email': teacher.email,
            'first_name': teacher.first_name,
            'last_name': teacher.last_name,
            'middle_name': teacher.middle_name or '',
            'educational_institution': teacher.educational_institution or '',
            'experience': teacher.experience or '',
            'specializations': teacher.specializations or '',
            'photo_url': teacher.photo.url if teacher.photo else None,
        },
        'favorites_count': favorites_count,
        'all_specializations': ALL_SPECIALIZATIONS,
    }

    return render(request, 'account/profile.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def upload_photo(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return JsonResponse({'success': False, 'message': 'Требуется авторизация'}, status=401)

    try:
        teacher = Teacher.objects.get(id=user_id)

        if 'photo' not in request.FILES:
            return JsonResponse({'success': False, 'message': 'Файл не найден'}, status=400)

        photo = request.FILES['photo']

        if not photo.content_type.startswith('image/'):
            return JsonResponse({'success': False, 'message': 'Файл должен быть изображением'}, status=400)

        if photo.size > 5 * 1024 * 1024:
            return JsonResponse({'success': False, 'message': 'Размер файла не должен превышать 5MB'}, status=400)

        allowed_types = ['image/jpeg', 'image/png', 'image/jpg']
        if photo.content_type not in allowed_types:
            return JsonResponse({'success': False, 'message': 'Допустимые форматы: JPG, PNG'}, status=400)

        if teacher.photo:
            try:
                if os.path.isfile(teacher.photo.path):
                    os.remove(teacher.photo.path)
            except:
                pass

        teacher.photo = photo
        teacher.save()

        if 'profile_data' in request.session:
            request.session['profile_data']['photo_url'] = teacher.photo.url
            request.session.modified = True

        return JsonResponse({
            'success': True,
            'photo_url': teacher.photo.url,
            'message': 'Фото успешно загружено'
        })

    except Teacher.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Пользователь не найден'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def remove_photo(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return JsonResponse({'success': False, 'message': 'Требуется авторизация'}, status=401)

    try:
        teacher = Teacher.objects.get(id=user_id)

        if teacher.photo:
            if os.path.isfile(teacher.photo.path):
                os.remove(teacher.photo.path)
            teacher.photo = None
            teacher.save()

            if 'profile_data' in request.session:
                request.session['profile_data']['photo_url'] = None
                request.session.modified = True

        return JsonResponse({'success': True, 'message': 'Фото удалено'})

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


def favorites(request):
    """Страница избранного"""
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('teachers:login')

    try:
        teacher = Teacher.objects.get(id=user_id)
    except Teacher.DoesNotExist:
        return redirect('teachers:login')

    favorites_list = Favorite.objects.filter(teacher=teacher).select_related('material').order_by('-created_at')

    favorites_data = []
    for fav in favorites_list:
        material = fav.material
        favorites_data.append({
            'id': fav.id,
            'material_id': material.id,
            'title': material.title,
            'description': material.description,
            'subject': material.subject.name if material.subject else '',
            'grade': material.grade.name if material.grade else '',
            'difficulty': material.difficulty.name if material.difficulty else '',
            'added_date': fav.created_at.strftime('%d.%m.%Y'),
            'url': material.file.url if material.file else '#',
        })

    context = {
        'user': teacher,
        'favorites': favorites_data,
        'favorites_count': len(favorites_data),
    }

    return render(request, 'account/favorites.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def add_to_favorites(request):
    """Добавление материала в избранное"""
    user_id = request.session.get('user_id')
    if not user_id:
        return JsonResponse({'success': False, 'message': 'Требуется авторизация'}, status=401)

    try:
        data = json.loads(request.body)
        material_id = data.get('material_id')

        if not material_id:
            return JsonResponse({'success': False, 'message': 'Не указан материал'})

        teacher = Teacher.objects.get(id=user_id)
        material = Material.objects.get(id=material_id)

        favorite, created = Favorite.objects.get_or_create(
            teacher=teacher,
            material=material
        )

        if created:
            return JsonResponse({
                'success': True,
                'message': 'Материал добавлен в избранное',
                'favorite_id': favorite.id,
                'favorites_count': Favorite.objects.filter(teacher=teacher).count()
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Материал уже в избранном'
            })

    except Teacher.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Пользователь не найден'}, status=404)
    except Material.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Материал не найден'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Неверный формат данных'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def remove_from_favorites(request, favorite_id):
    """Удаление материала из избранного по ID записи избранного"""
    user_id = request.session.get('user_id')
    if not user_id:
        return JsonResponse({'success': False, 'message': 'Требуется авторизация'}, status=401)

    try:
        teacher = Teacher.objects.get(id=user_id)

        # Ищем по ID записи избранного (favorite_id), а не по material_id
        favorite = Favorite.objects.get(id=favorite_id, teacher=teacher)

        favorite.delete()
        return JsonResponse({
            'success': True,
            'message': 'Удалено из избранного',
            'favorites_count': Favorite.objects.filter(teacher=teacher).count()
        })

    except Favorite.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Запись не найдена в избранном'
        }, status=404)
    except Teacher.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Пользователь не найден'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["GET"])
def get_favorites_list(request):
    """Получение списка ID избранных материалов пользователя"""
    user_id = request.session.get('user_id')
    if not user_id:
        return JsonResponse({'success': False, 'message': 'Требуется авторизация'}, status=401)

    try:
        teacher = Teacher.objects.get(id=user_id)
        favorites = Favorite.objects.filter(teacher=teacher).values_list('material_id', flat=True)

        return JsonResponse({
            'success': True,
            'favorites': list(favorites)
        })

    except Teacher.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Пользователь не найден'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["GET"])
def check_favorite(request, material_id):
    """Проверка, находится ли материал в избранном у пользователя"""
    user_id = request.session.get('user_id')
    if not user_id:
        return JsonResponse({'is_favorite': False})

    try:
        teacher = Teacher.objects.get(id=user_id)
        is_favorite = Favorite.objects.filter(teacher=teacher, material_id=material_id).exists()
        return JsonResponse({'is_favorite': is_favorite})
    except Teacher.DoesNotExist:
        return JsonResponse({'is_favorite': False})
    except Exception as e:
        return JsonResponse({'is_favorite': False})


@csrf_exempt
@require_http_methods(["POST"])
def clear_favorites(request):
    """Очистка всего избранного"""
    user_id = request.session.get('user_id')
    if not user_id:
        return JsonResponse({'success': False, 'message': 'Требуется авторизация'}, status=401)

    try:
        teacher = Teacher.objects.get(id=user_id)
        deleted_count, _ = Favorite.objects.filter(teacher=teacher).delete()

        return JsonResponse({
            'success': True,
            'message': 'Избранное очищено',
            'deleted_count': deleted_count
        })

    except Teacher.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Пользователь не найден'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


def get_favorites_stats(request):
    """Получение статистики по избранному"""
    user_id = request.session.get('user_id')
    if not user_id:
        return JsonResponse({'success': False, 'message': 'Требуется авторизация'}, status=401)

    try:
        teacher = Teacher.objects.get(id=user_id)
        count = Favorite.objects.filter(teacher=teacher).count()

        return JsonResponse({
            'success': True,
            'count': count
        })

    except Teacher.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Пользователь не найден'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

def help(request):
    """Страница помощи и поддержки"""
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('teachers:login')

    try:
        teacher = Teacher.objects.get(id=user_id)
    except Teacher.DoesNotExist:
        return redirect('teachers:login')

    favorites_count = Favorite.objects.filter(teacher=teacher).count()

    context = {
        'user': teacher,
        'favorites_count': favorites_count,
    }

    return render(request, 'account/help.html', context)