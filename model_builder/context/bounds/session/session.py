from typing import Protocol
from ..bounds import Boundedlike, session


class SessionBoundedlike(Boundedlike, Protocol):
    
    bound: session

class SessionBounded(SessionBoundedlike):

    bound : session = session