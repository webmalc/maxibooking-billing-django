from modeltranslation.translator import TranslationOptions, register

from .models import City, Country, Region


@register(Country)
class CountryTranslationOptions(TranslationOptions):
    fields = ('name', )
    required_languages = ('en', )


@register(Region)
class RegionTranslationOptions(TranslationOptions):
    fields = ('name', )
    required_languages = ('en', )


@register(City)
class CityTranslationOptions(TranslationOptions):
    fields = ('name', )
    required_languages = ('en', )
