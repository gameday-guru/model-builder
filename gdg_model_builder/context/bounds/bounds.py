from enum import Enum
from typing import Any, Protocol, Sequence


class Bound(Enum):
    EXECUTION = 1
    SESSION = 2
    USER = 3
    UNIVERSAL = 4

execution = Bound.EXECUTION
session = Bound.SESSION
user = Bound.USER
universal = Bound.UNIVERSAL

class Boundedlike(Protocol):

    bound : Bound

class Bounded(Boundedlike):

    bound : Bound


def fminb(l : Sequence[Any])->Bound:

    minimum = universal
    for obj in l:
        if isinstance(obj, Bound):
            if obj.value < minimum.value:
                minimum = obj

    return minimum

    