import time
from functools import lru_cache, partial, update_wrapper
from typing import Callable, TypeVar



def lru_cache_time(seconds : int, maxsize : int = 64):
    """
    Adds time aware caching to lru_cache
    """
    def wrapper(func : Callable)->Callable:
        
        @lru_cache(maxsize)
        def inner(__ttl, *args, **kwargs):
            # Note that __ttl is not passed down to func,
            # as it's only used to trigger cache miss after some time
            return func(*args, **kwargs)
        return lambda *args, **kwargs: inner(time.time() // seconds, *args, **kwargs) # this will reset over time because it is a different lambda when the floor division changes
    return wrapper
