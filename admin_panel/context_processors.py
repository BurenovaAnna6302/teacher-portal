# admin_panel/context_processors.py
from .constants import (
    EVENT_AUDIENCES, EVENT_FORMATS, EVENT_ACTIVITY_TYPES, EVENT_SUBJECTS,
    NEWS_STATUSES, NEWS_TARGET_AUDIENCES, NEWS_CONTENT_TYPES,
    MATERIAL_SUBJECTS, MATERIAL_TYPES, MATERIAL_DIFFICULTY, MATERIAL_GRADES,
    MATERIAL_FORMATS, MATERIAL_ASSESSMENT, MATERIAL_ADDITIONAL,
    DOCUMENT_CATEGORIES, DOCUMENT_LEVELS, DOCUMENT_YEARS,
    SURVEY_CATEGORIES, SURVEY_STATUSES
)

def admin_constants(request):
    return {
        'event_audiences': EVENT_AUDIENCES,
        'event_formats': EVENT_FORMATS,
        'event_activity_types': EVENT_ACTIVITY_TYPES,
        'event_subjects': EVENT_SUBJECTS,
        'news_statuses': NEWS_STATUSES,
        'news_target_audiences': NEWS_TARGET_AUDIENCES,
        'news_content_types': NEWS_CONTENT_TYPES,
        'material_subjects': MATERIAL_SUBJECTS,
        'material_types': MATERIAL_TYPES,
        'material_difficulty': MATERIAL_DIFFICULTY,
        'material_grades': MATERIAL_GRADES,
        'material_formats': MATERIAL_FORMATS,
        'material_assessment': MATERIAL_ASSESSMENT,
        'material_additional': MATERIAL_ADDITIONAL,
        'document_categories': DOCUMENT_CATEGORIES,
        'document_levels': DOCUMENT_LEVELS,
        'document_years': DOCUMENT_YEARS,
        'survey_categories': SURVEY_CATEGORIES,
        'survey_statuses': SURVEY_STATUSES,
    }