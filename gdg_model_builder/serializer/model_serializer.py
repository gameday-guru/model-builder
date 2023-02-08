import collections
from typing import Sequence, TypeVar, Generic
from .serializer import Serializer

K = TypeVar("K")
V = TypeVar("V")

class ModelSerializer(Serializer[K, V], Generic[K, V]):
    
    model_name : str
    state_name : str
    DELIMITER : str = ":::"
    encoding : str = "utf-8"
    
    def get_model_state_hash(self)->bytes:
        """_summary_

        Returns:
            bytes: _description_
        """
        return bytes(self.DELIMITER.join([
            self.model_name, 
            self.state_name
        ]), encoding=self.encoding)
    
    def model_hash(self, key : K)->bytes:
        """_summary_

        Args:
            key (K): _description_

        Returns:
            bytes: _description_
        """
        hash = self.hash(key)
        model_hash = self.DELIMITER.join([
            self.get_model_state_hash().decode(encoding=self.encoding),
            hash.decode(encoding=self.encoding)
        ])
        return bytes(model_hash, encoding=self.encoding)
    
    def model_unhash(self, key : bytes)->K:
        """_summary_

        Args:
            key (bytes): _description_

        Returns:
            K: _description_
        """
        hash_str = key.decode(encoding=self.encoding).split(self.DELIMITER)[-1]
        hash_bytes = bytes(hash_str, encoding=self.encoding)
        return self.unhash(hash_bytes)
    
    def __init__(self, *args, model_name : str, state_name : str, **kwargs) -> None:
        """Initializers a model serializer with a model_name and state_name.

        Args:
            model_name (str): is the name of the model.
            state_name (str): is the name of the state to which this applies.
        """
        super().__init__(*args, **kwargs)
        self.model_name = model_name
        self.state_name = state_name