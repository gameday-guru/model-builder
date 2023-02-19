from .redis_model_serializer import RedisModelSerializer
from typing import Sequence, TypeVar, Generic, Tuple, Iterable, Mapping

K = TypeVar("K")
V = TypeVar("V")

class RedisStagedModelSerializer(RedisModelSerializer[K, V],  Generic[K, V]):
    
    pass