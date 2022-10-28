import unittest
from .event import Event

class TestEvents(unittest.TestCase):

    def test_get_event_hash(self):
        
        # check event
        event = Event()
        ehash = event.get_event_hash()
        self.assertEqual(ehash, "e01bf5e1a06022103d51795629ccf770a7951f7a98986d7b3b7a021bbad6725e")
        
        # check dervied classe
        class Derivative(Event):
            pass
        deriative = Derivative()
        dhash = deriative.get_event_hash()
        self.assertNotEqual(ehash, dhash)
        
    def test_get_event_instance_hash(self):
        
        # check derived classes
        class MyEvent(Event):
            
            note : str
            
        a = MyEvent(note="abcdef")
        ahash = a.get_event_instance_hash()
        self.assertEqual(ahash, "0ed7105380491a2a9fe7108b8f4ef6d980ac55fddfd5eda22d47594b94e01035")
        
        b = MyEvent(note="abcdef")
        bhash = b.get_event_instance_hash()
        self.assertEqual(ahash, bhash)
        
        c = MyEvent(note="lkz")
        chash = c.get_event_instance_hash()
        self.assertNotEqual(chash, ahash)
        
