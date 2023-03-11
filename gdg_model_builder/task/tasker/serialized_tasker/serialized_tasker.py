from ..tasker import Tasker, K, V
from ....serializer.serializer import Serializer, ReadMode, WriteMode
from typing import Generic

class SerializedTasker(Tasker, Generic[V]):
    
    task_serializer : Serializer[V, V]
    lock_serializer : Serializer[K, bytes]
    progress_serializer : Serializer[K, float]    
    id : bytes
    
    async def send(self, *, task: V) -> V:
        
        # acquire the lock
        self.lock_serializer.stage(
            read=ReadMode.READ_THROUGH,
            write=WriteMode.WRITE_THROUGH
        )
        if self.lock_serializer[task] is not None:
            return self.get(task=task)
        self.lock_serializer[task] = self.id
        
        # check the lock
        if self.lock_serializer[task] == self.id:
            
            self.task_serializer.stage(write=WriteMode.WRITE_THROUGH)
            self.progress_serializer[task] = 0
            self.progress_serializer.commit()
            
            self.task_serializer.stage(write=WriteMode.WRITE_THROUGH)
            self.task_serializer[task] = task
            self.task_serializer.commit()
        
        return self.get(task=task)