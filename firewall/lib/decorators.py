from functools import wraps

from django.core.cache import cache


def cache_result(key, timeout=None):
    """
    Save function result in cache
    key - cache key
    timeout - cache timeout in seconds
    """

    def cache_decorator(func):
        @wraps(func)
        def func_wrapper(*args, **kwargs):
            cached_result = cache.get(key)
            if cached_result:
                return cached_result
            result = func(*args, **kwargs)
            cache.set(key, result, timeout)
            return result

        return func_wrapper

    return cache_decorator
