from ...struct import Struct

class ModelStruct(Struct):
    
    def struct_hash(self) -> bytes:
        return super().struct_hash()