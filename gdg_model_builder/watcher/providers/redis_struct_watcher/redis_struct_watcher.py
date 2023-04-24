from gdg_model_builder.structs import Struct
from ...log_mean_watcher import LogMeanWatcher
from ...weakref_watcher import WeakRefWatcher
from typing import TypeVar, Generic, Optional
import redis

S = TypeVar("S", Struct)

class RedisStructWatcher(WeakRefWatcher[S], LogMeanWatcher[S], Generic[S]):
    
    prefix : bytes 
    delim : str = ":::"
    encoding : str = "utf-8"
    store : redis.Redis
    
    async def update(self) -> Optional[S]:
        
        res = await self.poll()
        hash = res.struct_hash()
        
        # acquire lock
        if self.store.sismember(self.prefix, hash) == 1:
            res = None
        else:
            self.store.sadd(self.prefix, hash)
        # release lock  
            
        return res
        
        