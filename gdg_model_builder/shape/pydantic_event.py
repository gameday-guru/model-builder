from .pydantic_shape import PydanticShape

class PydanticEvent(PydanticShape):
   
    def hash(self) -> bytes:
        # now we are only hashing the timestamp
        return bytes(str(self._ts), encoding=self._encoding)
