from typing import Protocol

class Struct:
    
    def serialize(self)->bytes:
        pass
    
    def deserialize(self)->bytes:
        pass

    def struct_hash(self)->bytes:
        pass