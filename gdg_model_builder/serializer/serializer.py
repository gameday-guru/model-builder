import collections
from enum import Enum
from typing import Sequence, TypeVar, Generic, Dict, Tuple, Iterable, Optional

K = TypeVar("K")
V = TypeVar("V")

class ReadMode(Enum):
    READ_THROUGH = 0
    READ_LATENT = 1
    READ_CACHE = 2
    READ_CACHE_ONLY = 3

class WriteMode(Enum):
    WRITE_THROUGH = 0
    WRITE_CACHE = 1
    
class DeleteMode(Enum):
    DELETE_THROUGH = 0
    DELETE_CACHE = 1
    
class SaveMode(Enum):
    AUTO = 0
    SIGNED = 1
    MANUAL = 2

class Serializer(collections.UserDict[K, V], Generic[K, V]):
    
    def stage(self, /, *, 
            read : Optional[ReadMode],
            write : Optional[WriteMode],
            delete : Optional[DeleteMode]
        )->None:
        """Toggles stage mode.
        """
        pass
    
    def commit(self)->None:
        """Commits staged changes
        """
        pass 
    
    def unstage(self)->None:
        """Clears staged changes
        """
        pass
    
    def __getitem__(self, key : K)->Optional[V]:
        pass
    
    def __setitem__(self, key : K, value : V):
        pass
    
    def __delitem__(self, key : K):
        pass
    
    def __contains__(self, key : K):
        pass
    
    def serialize(self, value : V)->bytes:
        pass
    
    def deserialize(self, value : bytes)->V:
        pass
    
    def hash(self, key : K)->bytes:
        """Hashes a key for usage in storage.

        Args:
            key (K): is the original key.

        Returns:
            bytes: the hashed key.
        """
        pass
    
    def unhash(self, key : bytes)->K:
        """Hashes a key for usage in storage.

        Args:
            key (K): is the original key.

        Returns:
            bytes: the hashed key.
        """
        pass
    
    def entries(self)->Iterable[Tuple[K, V]]:
        """Gets a deterministic sequence of key and value tuples.

        Returns:
            Sequence[Tuple[K, V]]: a sequence of key and value pairs.
        """
        pass
    
    def values(self)->Iterable[V]:
        """Gets a deterministic sequence of values.

        Returns:
            Sequence[V]: a sequence of values.
        """
        pass
    
    def keys(self)->Iterable[K]:
        """Gets a deterministic sequence of keys.

        Returns:
            Sequence[K]: a sequence of keys.
        """
        pass
    
    def size(self)->int:
        """Gets a deterministic sequence of keys.

        Returns:
            Sequence[K]: a sequence of keys.
        """
        pass
    
    def empty(self)->None:
        """Gets a deterministic sequence of keys.

        Returns:
            Sequence[K]: a sequence of keys.
        """
        pass