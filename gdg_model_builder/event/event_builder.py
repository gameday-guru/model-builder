from typing import Sequence, TypeVar, Generic, Dict, Tuple, Iterable, Optional

K = TypeVar("K")
V = TypeVar("V") # this should be some kind of event

class EventBuilder(Generic[V]):
    pass