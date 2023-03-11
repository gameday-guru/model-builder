from typing import Protocol, TypeVar, Generic, Optional, Iterable, Iterator

V = TypeVar("V")

class CompletionStream(Iterator[Optional[V]], Protocol, Generic[V]):

    def is_complete(self)->bool:
        pass
    
    def next(self)->Optional[V]:
        pass
    
    def syn(self):
        pass
    
    def fin(self):
        pass
    
    def __next__(self) -> Optional[V]:
        
        if not self.is_complete():
            return None
        
        return self.next()