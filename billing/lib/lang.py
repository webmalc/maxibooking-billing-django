from django.utils.translation import get_language

DEFAULT_LANG = 'world'
LANGS = ('ru', )


def get_lang(lang=None):
    """
    Get current lang code
    """
    lang = get_language() if not lang else lang
    return lang if lang in LANGS else DEFAULT_LANG
