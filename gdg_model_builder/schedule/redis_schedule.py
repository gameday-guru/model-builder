from .weakref_schedule import WeakrefSchedule, S
from typing import Protocol, Callable, Awaitable, Generic, Optional
import redis
from pottery import Redlock, RedisSet
from gdg_model_builder.shape import Shape
import random
import asyncio
import datetime

class RedisSchedule(WeakrefSchedule, Generic[S]):
    
    store : redis.Redis
    group : bytes
    consumer_id : bytes
    Shape : type[S]
    
    # machine stack
    shape_todo_prefix : bytes = b'shape_todo:::'
    lock_prefix : bytes = b'locks:::'
    cycles_prefix : bytes = b'cycles:::'
    ts_prefix : bytes = b'ts:::'
    ts_todo_prefix : bytes = b'ts_todo:::'
    observations_prefix : bytes = b'observations:::'
    encoding : str = "UTF-8"

    
    def __init__(
        self, *, 
        store = redis.Redis(), 
        group : bytes = b"1",
        consumer_id : bytes = b"1",
        Shape : type[S] = Shape
    ) -> None:
        
        super().__init__()
        
        self.store = store
        self.group = group
        self.consumer_id = consumer_id
        self.Shape = Shape
    
    def get_shape_todo_key(self)->bytes:
        
        return self.shape_todo_prefix + self.group + self.Shape.identify()
    
    def get_cycles_key(self)->bytes:
        
        return self.cycles_prefix + self.group
        
    def get_cycles_lock_key(self)->bytes:
        """_summary_

        Returns:
            bytes: _description_
        """
        
        return self.lock_prefix + self.get_cycles_key()
        
    def get_cycles_lock(self)->Redlock:
        
        return Redlock(
            key=self.get_cycles_lock_key(),
            masters={self.store}
        )
        
    def get_ts_todo_key(self, *, ts : int, shape : S)->bytes:
        
        return self.ts_todo_prefix + bytes(f"{ts}", encoding=self.encoding) + shape.hash()
    
    def get_ts_todo_lock_key(self, *, ts : int, shape : S):
        
        return self.lock_prefix + self.get_ts_todo_key(ts=ts, shape=shape) 
    
    def get_ts_todo_lock(self, *, ts : int)->Redlock:
        
        return Redlock(
            key=self.get_ts_lock_key(ts=ts), #!!!!!! change
            masters={self.store}
        )
        
    def get_ts_key(self, *, ts : int)->bytes:
        
        return self.ts_prefix + bytes(f"{ts}", encoding=self.encoding)
    
    def get_ts_lock_key(self, *, ts : int):
        
        return self.lock_prefix + self.get_ts_key(ts=ts)
    
    def get_ts_lock(self, *, ts : int)->Redlock:
        
        return Redlock(
            key=self.get_ts_lock_key(ts=ts),
            masters={self.store}
        )
        
    def get_shape_ts_key(self, *, ts : int)->bytes:
        
        return self.ts_prefix + self.Shape.identify() + bytes(f"{ts}", encoding=self.encoding)
    
    def get_shape_ts_lock_key(self, *, ts : int):
        
        return self.lock_prefix + self.Shape.identify() + self.get_ts_key(ts=ts)
    
    def get_shape_ts_lock(self, *, ts : int)->Redlock:
        
        return Redlock(
            key=self.get_shape_ts_lock_key(ts=ts),
            masters={self.store}
        )
    
    def get_observations_key(self):
        
        return self.observations_prefix + self.Shape.identify()
    
    def get_observations_lock_key(self):
        
        return self.lock_prefix + self.get_observations_key()
    
    def get_observations_lock(self)->Redlock:
        
        return Redlock(
            key=self.get_observations_lock_key(),
            masters={self.store}
        )
        
    async def move_to_processing_stack(self, *, shape : S):
        pass
    
    async def remove_from_processing_stack(self, *, shape : S):
        pass
        
    async def push_time_independent(self, *, shape : S):
        
        # otherwise you're going to get the shape
        shape_ts_lock = self.get_shape_ts_lock(ts=-2)
        shape_ts_lock.acquire() #! lock
        
        # push the object to its apporpriate timestamp shape queue
        self.store.rpush(self.get_shape_ts_key(ts=-2), shape.serialize())
        
        # at this point, we're reading, so release all the locks
        shape_ts_lock.release() #? release
        
    async def push_time_dependent(self, *, shape : S):
        
        ts = shape.get_ts()
        
        # acquire the lock for the cycles
        cycles_lock = self.get_cycles_lock()
        cycles_lock.acquire() #! lock
        
        # get the lock for this timestamp overall
        ts_lock = self.get_ts_lock(ts=ts)
        ts_lock.acquire() #! lock
        
        # otherwise you're going to get the shape
        shape_ts_lock = self.get_shape_ts_lock(ts=ts)
        shape_ts_lock.acquire() #! lock
        
        # add cycle if the cycle for this timestamp doesn't exist
        self.store.zadd(self.get_cycles_key(), { ts : ts })
        
        # increment the number of operations on the timestamp
        self.store.incr(self.get_ts_key(ts=ts), 1)
        
        # push the object to its apporpriate timestamp shape queue
        self.store.rpush(self.get_shape_ts_key(ts=ts), shape.serialize())
        
        # at this point, we're reading, so release all the locks
        shape_ts_lock.release() #? release
        ts_lock.release() #? release
        cycles_lock.release() #? release
        
    async def push(self, *, shape : S)->Optional[S]:
        
        if shape.get_ts() < 0:
            await self.push_time_independent(shape=shape)
            return True
        else: 
            await self.push_time_dependent(shape=shape)
            return True
        
    async def pop_time_independent(self)->Optional[S]:
        
        shape_ts_lock = self.get_shape_ts_lock(ts=-1)
        shape_ts_lock.acquire() #! lock
        
        if self.store.llen(self.get_shape_ts_key(ts=-1)) < 1:
            shape_ts_lock.release()
            return None

        #! unsafe
        serialized_shape_backup = self.store.lrange(self.get_shape_ts_key(ts=-1), 0, 0)[0]
        # indicate that the shape has been read
        self.store.hset(self.get_shape_todo_key(), serialized_shape_backup,datetime.datetime.now().timestamp())
        
        # pop the shape off
        serialized_shape = self.store.lpop(self.get_shape_ts_key(ts=-1))
    
        shape_ts_lock.release() #? release
        
        if serialized_shape is None:
            return None
    
        return self.Shape.deserialize(serialized_shape)
        
    async def done(self, *, shape : S):
        
        #! unsafe, need to acquire lock
        self.store.hdel(self.get_shape_todo_key(), shape.serialize())
    
    async def pop_time_dependent(self)->Optional[S]:
        
        # acquire the lock for the cycles
        cycles_lock = self.get_cycles_lock()
        cycles_lock.acquire() #! lock
        
        if self.store.zcard(self.get_cycles_key()) < 1:
            cycles_lock.release()
            return None
        
        ts = int(self.store.zrange(self.get_cycles_key(), 0, 0)[0])
        
        # get the lock for this timestamp overall
        ts_lock = self.get_ts_lock(ts=ts)
        ts_lock.acquire() #! lock
        
        # if the length of time stamp is less than 0, your job is to get rid of it then run again
        ts_count = int(self.store.get(self.get_ts_key(ts=ts)))

        if ts_count is None or ts_count < 1:
            self.store.zrem(self.get_cycles_key(), ts)
            ts_lock.release() #? release
            cycles_lock.release() #? release
            return await self.pop_time_dependent()
        
        # otherwise you're going to get the shape
        shape_ts_lock = self.get_shape_ts_lock(ts=ts)
        shape_ts_lock.acquire() #! lock
        serialized_shape = self.store.lpop(self.get_shape_ts_key(ts=ts))
        if serialized_shape is not None:
            # if this shape was the one with a value
            self.store.decr(self.get_ts_key(ts=ts))
        
        # at this point, we're reading, so release all the locks
        shape_ts_lock.release() #? release
        ts_lock.release() #? release
        cycles_lock.release() #? release
         
        if serialized_shape is None:
            return None
    
        return self.Shape.deserialize(serialized_shape)
        
        
    async def pop(self)->Optional[S]:
        
        res = None
        flip = random.randint(0, 1)
        if flip:
            res = await self.pop_time_independent()
        else: 
            res = await self.pop_time_dependent()

            
        if res is None and flip:
            res = await self.pop_time_dependent()
        elif res is None and not flip:
            res = await self.pop_time_independent()
            
        return res
        
        
    async def emit(self, *, shape: S, force: bool = False) -> bool:
        
        if force:
            await self.push(shape=shape)
        
        # now where we actually care if the shape has been seen before
        shape_hash = shape.hash()
        lock = self.get_observations_lock()
        lock.acquire()
        
        observed_shape = self.store.sismember(
            self.get_observations_key(),
            shape_hash
        )
        
        if observed_shape:
            lock.release()
            return False
    
        await self.push(shape=shape)
        self.store.sadd(
            self.get_observations_key(),
            shape_hash
        )
        
        lock.release()
        
        
    async def sleep(self):
        pass
    
    async def handle_shape(self, *, shape : S):
        
        await asyncio.gather(*[
            cb(shape)
            for cb in self.cbs
        ])
        
    async def clean(self):
        
        self.store.flushall()
        
    async def tick(self):
        
        next = await self.pop()
        
        if next is not None:
            await self.handle_shape(shape=next)
            
            