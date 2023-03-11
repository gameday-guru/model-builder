import collections
from enum import Enum
from typing import Sequence, TypeVar, Generic, Dict, Tuple, Iterable, Optional, Protocol, Tuple

K = TypeVar("K")
V = TypeVar("V")

class Tasker(Protocol, Generic[V]):
    
    async def get(self, *, task : V)->Optional[V]:
        """Gets a task by id.

        Args:
            task_id (K): is the id for the task.

        Returns:
            V: the task (event) object.
        """
        raise NotImplementedError("get has not been implemented on this tasker.")
    
    async def send(self, *, task : V)->V:
        """Sends a task object.

        Args:
            task_id (K): is the id for the task.
            obj (V): is the task (event) object.

        Returns:
            V: is the event object that was sent.
        """
        raise NotImplementedError("send has not been implemented for this tasker.")
    
    async def has_sent(self, *, task : V)->bool:
        """Asserts whether the model has sent the task.

        Args:
            task_id (K): is the id of the task.

        Returns:
            bool: whether a task matching the id has been sent.
        """
        
        raise NotImplementedError("has_sent has not been implemented for this tasker.")
    
    async def set_progress(self, *, task : V)->float:
        """Sets the progress of a given task_id.

        Args:
            task_id (K): is the id of the task.

        Raises:
            NotImplementedError: _description_

        Returns:
            float: 0 to 1 float indicating percent progress of task. Negative value indicates task has not started.
        """
        raise NotImplementedError("set_progress has not been implemented for this tasker.")
    
    async def get_progress(self, *, task : V)->float:
        """Gets the progress of the task

        Args:
            task_id (K): the id of the task.

        Raises:
            NotImplementedError: _description_

        Returns:
            float: 0 to 1 float indicating percent progress of task. Negative value indicates the task has not started.
        """
        raise NotImplementedError("get_progress has not been implemented for this tasker.")
        
    async def has_started(self, *, task : V)->bool:
        """Asserts whether the task has started

        Args:
            task_id (K): is the id of the task.

        Raises:
            NotImplementedError: _description_

        Returns:
            bool: whether the task has started.
        """
        
        raise self.get_progress(task=task) > 0
    
    async def has_perished(self, *, task : V)->bool:
        raise NotImplementedError("has_perished has not been implemented for this tasker.")
        
    
    async def is_complete(self, *, task : V)->bool:
        return self.get_progress(task=task) >= 1.0
    
    async def emit(self, *, task : V)->V:
        
        if self.has_sent(task=task):
            return (await self.get(task=task)) or task
        
        return await self.send(task=task)
    