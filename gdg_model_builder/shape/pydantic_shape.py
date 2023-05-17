from .shape import Shape
from pydantic import BaseModel, Field, Extra, PrivateAttr
import datetime
import json
from typing_extensions import Self
from typing import ClassVar

class PydanticShape(BaseModel, Shape):
    _ts: int = PrivateAttr()
    _encoding: str = "UTF-8" # this should be included in the hash actually
    # because the encodings must be equivalent for logically equivalent objects
    # to be equivalent
    
    class Config:
        allow_population_by_field_name = True
        extra = Extra.ignore
        
    def __init__(self, **kwargs):
        BaseModel.__init__(self, **kwargs)
        self._ts = int(datetime.datetime.now().timestamp() * 1000)

    def serialize(self) -> bytes:
        return bytes(json.dumps(self.dict()), encoding=self._encoding)

    @classmethod
    def identify(cls) -> bytes:
        return bytes(f"{cls.__name__}", encoding=cls._encoding)

    @classmethod
    def deserialize(cls, serial: bytes) -> Self:
        return cls(**json.loads(serial.decode(encoding=cls._encoding)))

    def hash(self) -> bytes:
        return bytes(json.dumps(self.dict()), encoding=self._encoding)
    
    def overwrite_ts(self, now: int) -> None:
        self._ts = now

    def get_ts(self) -> int:
        return self._ts

