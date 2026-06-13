from django.contrib import admin
from django.core.cache import cache  # <-- ДОБАВЛЕНО: импорт кэша
from .models import PracticeCategory, Practice


@admin.register(PracticeCategory)
class PracticeCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'icon_color', 'sort_order']
    list_editable = ['sort_order']
    fields = ['name', 'icon', 'icon_color', 'sort_order']

    # АВТОМАТИЧЕСКАЯ ОЧИСТКА КЭША ПРИ СОХРАНЕНИИ
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        cache.clear()

    # АВТОМАТИЧЕСКАЯ ОЧИСТКА КЭША ПРИ УДАЛЕНИИ
    def delete_model(self, request, obj):
        super().delete_model(request, obj)
        cache.clear()


@admin.register(Practice)
class PracticeAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'audience', 'format_type', 'difficulty', 'created_date', 'is_published']
    list_filter = ['category', 'audience', 'format_type', 'difficulty', 'is_published']
    search_fields = ['title', 'short_description']
    list_editable = ['is_published']
    fieldsets = (
        ('Основная информация', {
            'fields': ('category', 'title', 'short_description', 'full_description')
        }),
        ('Дополнительные параметры', {
            'fields': ('audience', 'format_type', 'difficulty')
        }),
        ('Файл', {
            'fields': ('file',)
        }),
        ('Публикация', {
            'fields': ('created_date', 'is_published')
        }),
    )

    # АВТОМАТИЧЕСКАЯ ОЧИСТКА КЭША ПРИ СОХРАНЕНИИ
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        cache.clear()

    # АВТОМАТИЧЕСКАЯ ОЧИСТКА КЭША ПРИ УДАЛЕНИИ
    def delete_model(self, request, obj):
        super().delete_model(request, obj)
        cache.clear()