from typing import Protocol
from hashlib import sha256
from json import dumps

class Eventlike(Protocol):

    id : int

    def get_hash(self)->str:
        pass

class Event(Eventlike):
    
    id : int = 1

    @classmethod
    def get_hash(cls)->str:
        obj_hash = sha256()
        obj_hash.update(dumps(list(cls.__dict__.keys())).encode('utf-8'))
        obj_hash.update(cls.id.to_bytes(8, 'little'))
        return obj_hash.digest().hex()

    def get_event_instance_hash(self)->str:
        obj_hash = sha256()
        obj_hash.update(dumps(self.__dict__).encode('utf-8'))
        obj_hash.update(self.id.to_bytes(8, 'little'))
        return obj_hash.digest().hex()