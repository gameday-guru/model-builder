from typing import Protocol

from attr import frozen

from ..bounds.execution.execution import ExecutionBounded, ExecutionBoundedlike


class Executionlike(ExecutionBoundedlike, Protocol):

    # an id for the execution
    id : str

@frozen
class Execution(ExecutionBounded, ExecutionBoundedlike):

    # an id for the the exeuction
    id : str