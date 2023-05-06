from typing import Protocol
from typing_extensions import Self

class Shape: # shape can't be a protocol because this causes metaclass conflicts
    
    def serialize(self)->bytes:
        pass
    
    @classmethod
    def identify(cls)->bytes:
        pass
    
    @classmethod
    def deserialize(cls, serial : bytes)->Self:
        pass
    
    def hash(self)->bytes:
        pass
    
    def overwrite_ts(self, now : int)->None:
        pass
    
    def get_ts(self)->int:
        pass