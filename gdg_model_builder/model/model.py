from typing import Protocol
from typing import Any, Awaitable, Callable, Dict, List, Optional, Protocol, Sequence, TypeVar
from gdg_model_builder.state import State
from gdg_model_builder.shape import Shape
from gdg_model_builder.clock import Predicate
from gdg_model_builder.watcher import Observer

A = TypeVar("A", bound=Shape)
R = TypeVar("R", bound=Shape)
Method = Callable[[A], Awaitable[R]]
Task = Callable[[A], Awaitable[None]]
# Watcher = Callable[[], Awaitable[A]]
M = TypeVar("M", bound=Method)
T = TypeVar("T", bound=Task)
S = TypeVar("S", bound=Shape)
E = TypeVar("E", bound=Shape)

class Model(Protocol):
    
    def state(self, name : str, Shape : type[S])->State[S]:
        pass
    
    def method(self)\
        ->Callable[
            [M],
            M
        ]:
        """Binds a method to the model.
        """
        pass

    def task(self, Shape : type[E])\
        ->Callable[
            [Task[E]], 
            Task[E]
        ]:
        """Decorates a task, allowing it to be included in the distributed task loop.
        """
        pass
    
    def watch(self, Shape : Optional[type[S]], Event : Optional[type[E]])\
        ->Callable[
            [Observer[S]], 
            Observer[S]
        ]:
        """Binds a retrieviable state to the model
        """
        raise NotImplementedError("watch has not been implemented for this model class.")

    async def emit(self, shape : E, *, force : bool = False)->None:
        """Emits an event.
        """
        pass

    def run(self):
        """Starts the model
        """
        pass

    def period(self, predicate : Predicate, Event : type[E])->None:
        pass
    
    def now(self)->int:
        pass