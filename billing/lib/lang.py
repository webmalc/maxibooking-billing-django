from contextlib import contextmanager

from django.utils.translation import activate, get_language

DEFAULT_LANG = 'world'
LANGS = ('ru', )


def get_lang(lang=None):
    """
    Get current lang code
    """
    lang = get_language() if not lang else lang
    return lang if lang in LANGS else DEFAULT_LANG


@contextmanager
def select_locale(client=None, lang=None):
    try:
        old_lang = get_language()
        if not lang and client:
            lang = client.language
        if lang and lang != old_lang:
            activate(lang)

        yield None
    finally:
        if lang and lang != old_lang:
            activate(old_lang)
