from django.db import models


class Teacher(models.Model):
    """
    Педагог (Таблица 3 из диплома)
    """
    id = models.AutoField(primary_key=True, verbose_name='Идентификатор педагога')
    email = models.CharField(max_length=30, unique=True, verbose_name='Email')
    password = models.CharField(max_length=128, verbose_name='Пароль')

    # Личные данные
    last_name = models.CharField(max_length=30, verbose_name='Фамилия')
    first_name = models.CharField(max_length=30, verbose_name='Имя')
    middle_name = models.CharField(max_length=30, verbose_name='Отчество', blank=True, null=True)

    # Профессиональные данные
    educational_institution = models.CharField(max_length=200, verbose_name='Образовательное учреждение', blank=True, null=True)
    experience = models.IntegerField(verbose_name='Педагогический стаж', blank=True, null=True)
    category = models.CharField(max_length=50, verbose_name='Квалификационная категория', blank=True, null=True)
    specialization = models.CharField(max_length=50, verbose_name='Предметная специализация', blank=True, null=True)
    specializations = models.TextField(verbose_name='Предметные специализации (множественный выбор)', blank=True, null=True)
    photo = models.ImageField(upload_to='teachers/', verbose_name='Фото', blank=True, null=True)

    # Метаданные
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата регистрации')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        db_table = 'teacher'
        verbose_name = 'Педагог'
        verbose_name_plural = 'Педагоги'

    def __str__(self):
        return f"{self.last_name} {self.first_name} ({self.email})"

    def get_specializations_list(self):
        """Возвращает список выбранных специализаций"""
        if self.specializations:
            return self.specializations.split(',')
        return []

    def set_specializations_list(self, specializations_list):
        """Сохраняет список специализаций"""
        if specializations_list:
            self.specializations = ','.join(specializations_list)
        else:
            self.specializations = None