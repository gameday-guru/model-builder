from typing import Protocol
from ..bounds.session.session import SessionBoundedlike, SessionBounded


class Sessionlike(SessionBoundedlike, Protocol):

    # an id for the session
    id : str

    # a sub id to indicate the connection the session is making
    connection_id : str

    # time stamp for when the session expires
    exp : int

class Session(SessionBounded, SessionBoundedlike):

    # an id for the the exeuction
    id : str

    # time stamp for when the session expires
    exp : int