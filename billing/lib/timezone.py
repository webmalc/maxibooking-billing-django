from timezonefinder import TimezoneFinder

tf = TimezoneFinder()


def get_timezone(latitude: float = None, longitude: float = None,
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
