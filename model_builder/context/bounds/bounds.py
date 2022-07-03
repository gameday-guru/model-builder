from enum import Enum
from typing import Protocol, Sequence, Any

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

class BoundsReificationlike(Protocol):

    @staticmethod
    def fminb(l : Sequence[Any])->Bound:
        pass

class BoundsReification(BoundsReificationlike):

    @staticmethod
    def fminb(l : Sequence[Any])->Bound:

        min = universal
        for obj in l:
            if isinstance(obj, Bound):
                if obj.value < min.value:
                    min = obj
            elif issubclass(obj, Bounded):
                if obj.bound.value < min.value:
                    min = obj.bound

        return min
