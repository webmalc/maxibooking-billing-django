from modeltranslation.translator import TranslationOptions, register

from .models import Order, Service


@register(Service)
class ServiceTranslationOptions(TranslationOptions):
    fields = ('title', 'description')
    required_languages = ('en', )


@register(Order)
class OrderTranslationOptions(TranslationOptions):
    fields = ('note', )
