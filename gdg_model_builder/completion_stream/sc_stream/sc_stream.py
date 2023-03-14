from ..completion_stream import CompletionStream, V
from gdg_model_builder.serializer.serializer import Serializer, WriteMode, ReadMode
from typing import Optional, Generic, List, Dict, MutableSet, TypeVar, Mapping, Sequence
from gdg_model_builder.lock.lock import Lock
from time import sleep

T = TypeVar("T")

class SerializerStream(CompletionStream[V], Generic[V, T]):
    
    event_lock : Lock[V]
    
    cycle_queue : List[T] # min heap    
    cycle_sets : Mapping[T, Serializer[V, float]]
    queue_lock : Lock[int]
    
    read_set : MutableSet[V]    
    times : Mapping[V, MutableSet[T]]
    ready_queue : List[V]
    
    def send(self, *, event: V, cycle : T):
        
        if self.event_lock.test(event):
            self.cycle_queue.append(cycle)
            self.cycle_sets[cycle][event][-1.0]
        
    def is_ready(self, *, event : V):
        
        t0 = self.cycle_queue[0]
        if not event in self.cycle_sets[self.cycle_queue[0]]:
            return False
        
        self.times[event].add(t0)
        return True
    
    def syn(self, *, event : V):
        
        self.set_progress(event, 0.0)
        
    def set_progress(self, *, event : V, pct : float):
        
        for time in self.times[event]:
            self.cycle_sets[time][event] = pct
        
    def fin(self, event : V):
        
        for time in self.times[event]:
            
            del self.cycle_sets[time][event]
            
            while len(self.cycle_queue[time]) > 0:
                sleep(0)
            
            if time == self.cycle_queue[0] and self.queue_lock.test(0):
                self.cycle_queue.pop(0)
                
            self.times[event].remove(time)
        
    def __next__(self) -> Optional[V]:
        
        for event in self.read_set:
            if self.is_ready(event):
                self.ready_queue(event)
        
        if len(self.ready_queue > 0):
            return self.ready_queue.pop(0)
        
        return None
        
        

    