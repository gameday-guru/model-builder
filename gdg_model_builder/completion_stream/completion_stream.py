from typing import Protocol, TypeVar, Generic, Optional, Iterable, Iterator

V = TypeVar("V")
T = TypeVar("T")

class CompletionStream(Iterator[Optional[V]], Protocol, Generic[V]):
    
    
    def send(self, *, event : V):
        pass
    
    def syn(self, *, event : V):
        pass
    
    def set_progress(self, *, event : V, pct : float):
        pass
    
    def fin(self, *, event : V):
        pass
    
    def __next__(self) -> Optional[V]:
        
        pass