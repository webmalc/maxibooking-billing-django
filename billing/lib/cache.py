"""
The cache utilities
"""
from functools import wraps

from django.core.cache import cache


def cache_result(func):
    """
    The decorator for caching the function result
    """

    @wraps(func)
    def with_cache(*args, **kwargs):
        """
        Cached function
        """
        key = '{}{}{}'.format(
            hash(func), hash(args), hash(frozenset(kwargs.items())))

        cached_result = cache.get(key)
        if cached_result is not None:
            return cached_result if cached_result != 'None' else None
        result = func(*args, **kwargs)
        cache.set(key, result if result is not None else 'None')

        return result

    return with_cache
