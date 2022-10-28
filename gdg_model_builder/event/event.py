from enum import Enum
from typing import Protocol, Optional
from hashlib import sha256
from json import dumps
from typing_extensions import Self

class Particul(Enum):
    shared = 0
    exclusive = 1
    iproxy = 2
    pproxy = 3
    
shared = Particul.shared
exclusive = Particul.exclusive
iproxy = Particul.iproxy
pproxy = Particul.pproxy


class Eventlike(Protocol):

    id : int = 0
    nonce : bool = True
    model_hostname : Optional[str] = None
    particul : Particul = Particul.exclusive
    
    def __init__(self, **kwargs) -> None:
        super().__init__()
        self.__dict__.update(kwargs)
        
    def update_from_dict(self, **kwargs) -> Self:
        self.__dict__.update(kwargs)
        return self
    
    @classmethod
    def get_event_hash(cls)->str:
        obj_hash = sha256()
        obj_hash.update(cls.__name__.encode('utf-8'))
        obj_hash.update(dumps(list(cls.__dict__.keys())).encode('utf-8'))
        obj_hash.update(str(cls.id).encode('utf-8'))
        obj_hash.update(str(cls.particul).encode('utf-8'))
        res = obj_hash.digest().hex()
        return res

    def get_event_instance_hash(self)->str:
        cls = self.__class__
        obj_hash = sha256()
        obj_hash.update(cls.__name__.encode('utf-8'))
        obj_hash.update(dumps(self.__dict__).encode('utf-8'))
        obj_hash.update(str(cls.particul).encode('utf-8'))
        return obj_hash.digest().hex()

class Event(Eventlike):
    
    id : int = 1
    nonce : bool = True
    model_hostname : Optional[str] = None
    particul : Particul = Particul.exclusive
    
    def __init__(self, **kwargs) -> None:
        super().__init__()
        self.__dict__.update(kwargs)
        
    def update_from_dict(self, **kwargs) -> Self:
        self.__dict__.update(kwargs)
        return self
    
    @classmethod
    def get_event_hash(cls)->str:
        obj_hash = sha256()
        obj_hash.update(cls.__name__.encode('utf-8'))
        obj_hash.update(dumps(list(cls.__dict__.keys())).encode('utf-8'))
        obj_hash.update(str(cls.id).encode('utf-8'))
        obj_hash.update(str(cls.particul).encode('utf-8'))
        res = obj_hash.digest().hex()
        return res

    def get_event_instance_hash(self)->str:
        cls = self.__class__
        obj_hash = sha256()
        obj_hash.update(cls.__name__.encode('utf-8'))
        obj_hash.update(dumps(self.__dict__).encode('utf-8'))
        obj_hash.update(str(cls.particul).encode('utf-8'))
        return obj_hash.digest().hex()
