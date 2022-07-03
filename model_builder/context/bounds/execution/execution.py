from typing import Protocol
from ..bounds import Boundedlike, execution


class ExecutionBoundedlike(Boundedlike, Protocol):
    
    bound: execution

class ExecutionBounded(ExecutionBoundedlike):

    bound : execution = execution