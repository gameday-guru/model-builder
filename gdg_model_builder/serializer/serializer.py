import collections
from typing import Sequence, TypeVar, Generic, Dict, Tuple, Iterable, Optional

K = TypeVar("K")
V = TypeVar("V")

class Serializer(collections.UserDict[K, V], Generic[K, V]):
    
    def stage(self)->None:
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