from timezonefinder import TimezoneFinder

tf = TimezoneFinder()

RESULT_TIMEZONE_OVERWRITE = {'Asia/Qostanay': 'Asia/Almaty'}


def get_timezone_strict(latitude: float = None,
                        longitude: float = None,
                        city=None) -> str:
    """
    Get timezone by city or coordinates
    """
    if city:
        latitude = city.latitude
        longitude = city.longitude

    if not latitude and not longitude:
        raise ValueError(
            'Neither the coordinates nor the city are not specified.')

    timezone = tf.certain_timezone_at(lng=longitude, lat=latitude)
    if not timezone:
        timezone = tf.closest_timezone_at(lng=longitude, lat=latitude)

    return timezone


def get_timezone(latitude: float = None, longitude: float = None,
                 city=None) -> str:
    timezone = get_timezone_strict(latitude, longitude, city)
    return RESULT_TIMEZONE_OVERWRITE.get(timezone, timezone)
