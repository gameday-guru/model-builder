from typing import Protocol
from ..execution.execution import Executionlike
from ..user.user import Userlike
from ..session.session import Sessionlike
from attrs import frozen

class Contextlike(Protocol):

    execution : Executionlike

    session : Sessionlike

    user : Userlike

@frozen
class Context(Contextlike): 
    
    execution : Executionlike

    session : Sessionlike

    user : Userlike
