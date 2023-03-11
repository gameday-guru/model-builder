from ..completion_stream import CompletionStream, V
from gdg_model_builder.serializer.serializer import Serializer, WriteMode, ReadMode
from typing import Optional, Generic, List

class SerializerStream(CompletionStream, Generic[V]):
    
    curr : Serializer[int, V]
    complete : Serializer[V, int]
    queue : List[V]
    num_times : int
    
    def is_complete(self) -> bool:
        return self.complete[self.curr[0]] > 0
    
    def syn(self):
        
        self.complete.stage(
            read=ReadMode.READ_THROUGH,
            write=WriteMode.WRITE_THROUGH
        )
        
        self.curr.stage(
            read=ReadMode.READ_THROUGH,
            write=WriteMode.WRITE_THROUGH
        )
        
        status = self.complete[self.curr[0]]
        if status is not None:
            return
        # TODO: we'll want to check if we care about race condition here later
        self.complete[self.curr[0]] = 0
        self.complete.commit()
        
    def fin(self):
        
        self.complete.stage(
            read=ReadMode.READ_THROUGH,
            write=WriteMode.WRITE_THROUGH
        )
        
        self.curr.stage(
            read=ReadMode.READ_THROUGH,
            write=WriteMode.WRITE_THROUGH
        )
        
        status = self.complete[self.curr[0]]
        if status is None:
            return
        # TODO: we'll want to check if we care about race condition here later
        self.complete[self.curr[0]] = status + 1 

    