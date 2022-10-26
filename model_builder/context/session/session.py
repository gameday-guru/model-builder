from typing import Protocol

from attr import frozen

from ..bounds.session.session import SessionBounded, SessionBoundedlike


class Sessionlike(SessionBoundedlike, Protocol):

    # an id for the session
    id : str

    # a sub id to indicate the connection the session is making
    connection_id : str

    # time stamp for when the session expires
    exp : int

@frozen
class Session(SessionBounded, SessionBoundedlike):

    # an id for the the exeuction
    id : str

    # time stamp for when the session expires
    exp : int