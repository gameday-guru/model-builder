from typing import Protocol
from ..bounds import Boundedlike, user


class UserBoundedlike(Boundedlike, Protocol):
    
    bound: user

class UserBounded(UserBoundedlike):

    bound : user = user