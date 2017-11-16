from django.conf import settings
from django.utils import translation


def auto_populate(obj, field_name, value_getter):
    """
    Auto populate translatable fields
    """
    lang = translation.get_language()
    try:
        for code, title in settings.LANGUAGES:
            translation.activate(code)
            setattr(obj, field_name + '_' + code, value_getter())
    finally:
        translation.activate(lang)

    return obj
