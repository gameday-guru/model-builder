from typing import Protocol

from attr import frozen

from ..bounds.user.user import UserBounded, UserBoundedlike


class Userlike(UserBoundedlike, Protocol):

    # an id for the user
    id : str

    # a sub id to indicate the connection the user is making
    connection_id : str

@frozen
class User(UserBounded, UserBoundedlike):

    # an id for the the exeuction
    id : str

    # a sub id to indicate the connection the user is making
    connection_id : str