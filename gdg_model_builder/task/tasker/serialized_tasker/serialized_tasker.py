from ..tasker import Tasker, K, V
from ....serializer.serializer import Serializer, ReadMode, WriteMode
from gdg_model_builder.lock.lock import Lock
from typing import Generic

class SerializedTasker(Tasker, Generic[V]):
    
    task_serializer : Serializer[V, V]
    lock : Lock[K, bytes]
    progress_serializer : Serializer[K, float]    
    
    async def send(self, *, task: V) -> V:
        
        if not self.lock.test(task):
            return self.get(task=task)
        
        self.progress_serializer.stage(write=WriteMode.WRITE_THROUGH)
        self.progress_serializer[task] = 0
        self.progress_serializer.commit()
        
        self.task_serializer.stage(write=WriteMode.WRITE_THROUGH)
        self.task_serializer[task] = task
        self.task_serializer.commit()
        
        return self.get(task=task)