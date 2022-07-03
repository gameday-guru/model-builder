from typing import Protocol
from hashlib import sha256
from json import dumps

class Eventlike(Protocol):

    id : int

    async def get_hash(self)->str:
        pass

class Event(Eventlike):
    
    id : int = 1

    @classmethod
    async def get_hash(cls)->str:
        hash = sha256()
        hash.update(dumps(cls.__dict__.keys()))
        hash.update(cls.id)
        return hash.digest().hex()