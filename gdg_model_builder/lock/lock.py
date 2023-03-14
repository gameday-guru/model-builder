from typing import Protocol, Generic, TypeVar

K = TypeVar("K")
V = TypeVar("V")

class Lock(Protocol, Generic[K, V]):
    
    
    def acquire(self, *, loc=K):
        pass
    
    def release(self, *, loc=K):
        pass
    
    def test(self, *, loc=K)->bool:
        pass