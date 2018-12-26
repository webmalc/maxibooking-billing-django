from django.conf import settings


def get_settings(param_name, country=None, client=None):
    """
    Return MB settings
    """

    def default():
        return getattr(settings, param_name)

    if not client and not country:
        country = '__all__'
    if not country and client:
        country = client.country.tld
    if not isinstance(country, str):
        country = country.tld
    param = settings.MB_SETTINGS_BY_COUNTRY.get(param_name, None)
    if not param:
        return default()

    country = settings.MB_COUNTRIES_OVERWRITE.get(country, country)
    param_country = param.get(country, None)
    if not param_country:
        param_country = param.get('__all__', None)
    if not param_country:
        return default()
    return param_country
