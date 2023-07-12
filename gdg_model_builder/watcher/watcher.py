import asyncio
from gdg_model_builder.shape import Shape
from typing import Protocol, Generic, TypeVar, Callable, Awaitable, Tuple
import datetime

S = TypeVar("S", bound=Shape)
E = TypeVar("E", bound=Shape)
Observer = Callable[[], Awaitable[S]]
Translator = Callable[[S], Awaitable[E]]
EventHandler = Callable[[E], Awaitable[None]]

class Watcher(Generic[S, E]):
    shape: type[S]
    event: type[E]
    observer: Observer[S]
    translator: Translator[S, E]
    id: str
    handlers: set[EventHandler[E]]

    def __init__(
        self, *, shape: type[S], event: type[E], observer: Observer[S],
        translator: Translator[S, E], id: str = "root"
    ) -> None:
        self.shape = shape
        self.event = event
        self.observer = observer
        self.translator = translator
        self.id = id
        self.handlers = set()

    async def is_new(self, shape: S) -> bool:
        pass

    def add_handler(self, handler: EventHandler[E]):
        self.handlers.add(handler)

    def remove_handler(self, handler: EventHandler[E]):
        self.handlers.remove(handler)

    async def handle_event(self, event: E):
        tasks = [handler(event) for handler in self.handlers]
        await asyncio.gather(*tasks)

    async def tick(self, *, force : bool = False) -> Tuple[bool, S]:
        result = await self.observer()
        if not force and not await self.is_new(result):
            return (False, result)
        event = await self.translator(result)
        await self.handle_event(event)
        return (True, result)
    
    def now(self)->int:
        return int(datetime.datetime.now().timestamp() * 1000)
    
    async def clean(self):
        pass
        
        