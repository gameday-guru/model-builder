from typing import Protocol
from ..bounds.user.user import UserBoundedlike, UserBounded


class Userlike(UserBoundedlike, Protocol):

    # an id for the user
    id : str

    # a sub id to indicate the connection the user is making
    connection_id : str

class User(UserBounded, UserBoundedlike):

    # an id for the the exeuction
    id : str

    # a sub id to indicate the connection the user is making
    connection_id : str