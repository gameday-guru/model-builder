from ..serialized_listener.serialized_listener import SerializedListener
from ..cbq_listener.cbq_listener import CbqListener
from ..sleepy_listener.sleepy_listener import SleepyListener
from gdg_model_builder.serializer.serializer import Serializer

class StdListener(SerializedListener, CbqListener, SleepyListener):
    
    def __init__(self, *, store : Serializer, sleep : int) -> None:
        CbqListener.__init__()
        SerializedListener.__init__(self, store=store)
        SleepyListener.__init__(self, sleep=sleep)
        