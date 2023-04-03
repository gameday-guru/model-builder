from pydantic import BaseModel

class Struct(BaseModel):

    def struct_hash(self)->bytes:
        pass