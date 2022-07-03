from typing import Protocol
from ..bounds.execution.execution import ExecutionBoundedlike, ExecutionBounded


class Executionlike(ExecutionBoundedlike, Protocol):

    # an id for the execution
    id : str

class Execution(ExecutionBounded, ExecutionBoundedlike):

    # an id for the the exeuction
    id : str