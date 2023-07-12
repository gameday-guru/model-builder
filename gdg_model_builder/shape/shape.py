from typing import Protocol
from typing_extensions import Self
from gdg_model_builder.util import Symbol

class Shape(Symbol): # shape can't be a protocol because this causes metaclass conflicts
    
    def serialize(self)->bytes:
        pass
    
    @classmethod
    def identify(cls)->bytes:
        return bytes(f"{cls.__name__}", encoding="utf-8")
    
    @classmethod
    def deserialize(cls, serial : bytes)->Self:
        pass
    
    def hash(self)->bytes:
        pass
    
    def overwrite_ts(self, now : int)->None:
        pass
    
    def get_ts(self)->int:
        pass
    
    @classmethod
    def from_dict(cls, **kwargs)->Self:
        pass