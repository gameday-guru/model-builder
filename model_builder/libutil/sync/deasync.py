from typing import TypeVar, Callable, Coroutine, Any
import asyncio

AsyncCallable = Callable[..., Coroutine[Any, Any, Any]]

A = TypeVar("A", bound=AsyncCallable)
C = TypeVar("C", bound=Callable)

class DeasyncCallable(Callable):
    bypass : Callable

def deasync(f : A)->C:
    """Transforms an async method into a synchronous one.

    :param f: is the method.
    :type f: A is a AsyncCallable
    :return: the synchronous equivalent of the method.
    :rtype: C is the Callable equivalent of the AsyncCallable.
    """
    def wrapper(*args, **kwargs):
        coro = asyncio.coroutine(f)
        future = coro(*args, **kwargs)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(future)

    wrapper.bypass = f
    return wrapper