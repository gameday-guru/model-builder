from datetime import datetime
import time
from typing import Any, Awaitable, Callable, Dict, List, Optional, Protocol, Sequence, TypeVar
from pydantic import BaseModel

from gdg_model_builder.context.context.context import Context, get_min_key
from gdg_model_builder.context.user.user import Userlike
from gdg_model_builder.event.event import Event
from collections.abc import Iterable

##################
### Type Vars ####
##################
P = TypeVar("P")
R = TypeVar("R")
BaseModelVar = TypeVar("BaseModelVar", bound=BaseModel) # base model return
EventVar = TypeVar("EventVar", bound=Event)

AsyncArityOne = Callable[[P], Awaitable[R]]
AsyncCtxualGenerator = Callable[[Context], Awaitable[R]]
AsyncCtxualTransformer = Callable[[Context, R], Awaitable[R]]
AsyncWatcherGenerator = Callable[[Context], Awaitable[Iterable]]

EO = Callable[[Event, Context], Awaitable[R]]

# watcher types
WA = Callable[[], Sequence[R]]
WT = Callable[[Event, Context], Awaitable[R]]

LA = Callable[[float, Optional[float]], float]

LA = Callable[[float, Optional[float]], float]

class CronEvent(Event):
    """A Cron Event is an event with a time stamp
    """
    
    ts : float
    valid : LA
    
class Init(Event):
    """An Init event is an event that has init set to 1.
    """
    
    init : int = 1

class Modellike(Protocol):

    def method(self, func : AsyncArityOne)\
        ->Callable[
            [AsyncArityOne],
            AsyncArityOne
        ]:
        """Binds a method to the model.
        """
        pass

    def get(self, key : str, *args, Struct : type[R])\
        ->Callable[
            [AsyncCtxualTransformer[R]],
            AsyncCtxualGenerator[R]
        ]:
        """Binds a retrieviable state to the model
        """
        pass

    def set(self, key : str, *args, Struct : type[R])\
        ->Callable[
            [AsyncCtxualTransformer[R]], 
            AsyncCtxualTransformer[R]
        ]:
        """Decorates a setter, allowing it to perform state management
        """
        pass

    def task(self, *args, Event : Optional[type[EventVar]] = None, valid : Optional[LA] = None)\
        ->Callable[
            [Callable[[EventVar, Context], Awaitable[R]]], 
            Callable[[EventVar, Context], Awaitable[R]]
        ]:
        """Decorates a task, allowing it to be included in the distributed task loop.
        """
        pass
    
    def watch(self, *args, Event : type[EventVar])\
        ->Callable[
            [Callable[[EventVar, Context], Awaitable[R]]], 
            Callable[[EventVar, Context], Awaitable[R]]
        ]:
        """Binds a retrieviable state to the model
        """
        raise NotImplementedError("watch has not been implemented for this model class.")

    def watch_task(self, *args, Event : type[EventVar], watcher=Optional[AsyncWatcherGenerator])\
        ->Callable[
            [Callable[[EventVar, Context], Awaitable[R]]], 
            Callable[[EventVar, Context], Awaitable[R]]
        ]:
        """
        Watches for new entries in an iterator and runs the task when there are new entries
        """
        raise NotImplementedError("watch_task has not been implemented for this model class.")

    def emit(self, event : Event)->None:
        """Emits an event.
        """
        pass

    def acl(self, key : str, /)->str:
        """Creates an acl at a given key.
        """
        pass

    def join_acl(self, *, key : str, user : Userlike)->str:
        """Adds a user to an AsyncArityOneL.
        """
        pass

    async def start(self):
        """Starts the model
        """
        pass
    
    async def sim(self):
        """Simulates the model
        """
        pass
    