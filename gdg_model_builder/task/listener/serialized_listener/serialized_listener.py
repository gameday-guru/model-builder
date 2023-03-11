from ..listener import Listener, V
from typing import Generic, Iterable
from ....serializer.serializer import Serializer

class SerializedListener(Listener, Generic[V]):
    
    store : Serializer[V, V]
    
    def __init__(self, *, store : Serializer[V, V]) -> None:
        super().__init__()
        self.store = store
    
    async def get_events(self) -> Iterable[V]:
        return self.store.values()