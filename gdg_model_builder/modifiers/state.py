"""Modifier flags for the Model state routes.
"""
from enum import Enum


class Privilege(Enum):
    """_summary_

    Args:
        Enum (_type_): _description_
    """
    
    PRIVATE = "private"
    PUBLIC = "public"
    
    """
    UNIPRIVATE = 2
    UNIPUBLIC = 3
    
    USERPRIVATE = 4
    USERPUBLIC = 5
    
    SESSIONPUBLIC = 6
    SESSIONPRIVATE = 7
    
    EXECUTIONPUBLIC = 8
    EECUTIONPRIVATE = 9
    """
    
    
private = Privilege.PRIVATE
public = Privilege.PUBLIC

class Appendage(Enum):
    """_summary_

    Args:
        Enum (_type_): _description_
    """
    
    LIKABLE = 0 # whether or not the state can be liked (like boolean field can be appended to the state)
    FLAGGABLE = 1 # whether or not an arbitrary flag can be appended to the state 
    
    TRAFFICABLE = 3 # whether or not a traffic count can be appended to the state
    COUNTABLE = 4 # whether or not an arbitrary count can be appended ot the state
    
    APPENDABLE = 5 # whether or not an arbitrary appendage can be added to the state
