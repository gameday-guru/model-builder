from typing import Any, Dict, Protocol, Sequence

from attrs import frozen

from ..bounds.bounds import Bound, fminb
from ..execution.execution import Executionlike
from ..session.session import Sessionlike
from ..user.user import Userlike


class Contextlike(Protocol):

    execution : Executionlike

    session : Sessionlike

    user : Userlike
    
    key : str
    
    target : Bound

class ContextkeyException(Exception):
    pass

@frozen
class Context(Contextlike): 
    
    execution : Executionlike

    session : Sessionlike

    user : Userlike
    
    key : str
    
    target : Bound
    
    
def get_bounds_keys(context : Contextlike) -> Dict[Bound, str]:
    """Gets the keys for a set of bounds

    Args:
        context (Contextlike): _description_

    Returns:
        Dict[Bound, str]: _description_
    """
    
    universal = context.key
    user = f"{universal}:{context.user.id}"
    session = f"{user}:{context.session.id}"
    execution = f"{session}:{context.execution.id}"
    
    return {
        Bound.EXECUTION : execution,
        Bound.SESSION : session,
        Bound.USER : user,
        Bound.UNIVERSAL : universal
    }

def get_min_key(*, bounds : Sequence[Any], key : str, context : Contextlike) -> str:
    """Gets the minimum key for a key given a context.
    
    key checking helps to catch framework errors and route corruption.

    Args:
        bounds (Sequence[Any]): _description_
        key (str): _description_
        context (Contextlike): _description_

    Raises:
        ContextkeyException: _description_

    Returns:
        str: _description_
    """
    """
    if key != context.key:
        raise ContextkeyException()
    """
    
    min_bound = fminb(bounds)
    if min_bound.value > context.target.value:
        min_bound = context.target

        
    return get_bounds_keys(context)[min_bound] or context.key

        
