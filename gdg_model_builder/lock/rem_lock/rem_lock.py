from ..lock import Lock, V, K
from gdg_model_builder.serializer.serializer import Serializer
from typing import Generic
from time import sleep

class RemLock(Lock[K, V], Generic[K, V]):
    
    id : V
    serializer : Serializer[K, V]
    
    def __init__(self, *, id : V, serializer : Serializer) -> None:
        super().__init__()
        self.id = id
        self.serializer = serializer
        
    def acquire(self, *, loc : K):
        
        while True:
            sleep(0)
            if self.test(loc=loc):
                return
        
    
    def release(self, *, loc : K):
        
        if self.test():
            del self.serializer[loc]
              
    
    def test(self, * loc : K) -> bool:
        
        while True:
            
            lock = self.serializer[loc]
            
            if lock is not None:
                return lock == self.id
            
            self.serializer[loc] = self.id
            self.serializer.commit()
        