from typing import Iterable, TypeVar, List, Generic
from weakref import WeakKeyDictionary
from gdg_model_builder.util import Symbol

V = TypeVar("V")
BUFFERIZED_DICT : WeakKeyDictionary[Symbol, List] = WeakKeyDictionary()
DEBUFFERIZED_DICT : WeakKeyDictionary[Symbol, List] = WeakKeyDictionary()

async def bufferized(symbol : Symbol, iter : Iterable[V], size : int)->List[V]:
    if symbol not in BUFFERIZED_DICT:
        BUFFERIZED_DICT[symbol] = []
   
    for v in iter:
        BUFFERIZED_DICT[symbol].append(v)
        
    return [
        BUFFERIZED_DICT[symbol].pop(0)
        for i in range(size)
    ]

async def debufferized(symbol : Symbol, iter : Iterable[V])->V:
    if symbol not in DEBUFFERIZED_DICT:
        DEBUFFERIZED_DICT[symbol] = []
   
    for v in iter:
        DEBUFFERIZED_DICT[symbol].append(v)
        
    return DEBUFFERIZED_DICT[symbol].pop(0)