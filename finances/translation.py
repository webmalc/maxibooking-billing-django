from modeltranslation.translator import TranslationOptions, register

from .models import Service


@register(Service)
class TechnologyTranslationOptions(TranslationOptions):
    fields = ('title', 'description')
    required_languages = ('en', )
