import unittest
from gdg_model_builder.util.deasync import deasync
from .pydantic_shape import PydanticShape
from time import sleep

class TestRedisSchedule(unittest.TestCase):

    def test_pydantic_shape(self):
        
        class Score(PydanticShape):
           home : int
           away : int
           
        score = Score(home=1, away=2)
        
        sleep(1)
    
        another_score = Score(home=1, away=2)
        
        self.assertEqual(
            score.hash(),
            another_score.hash()
        )
        
        self.assertEqual(
            score.serialize(),
            another_score.serialize()
        )
        
        self.assertNotEqual(
            score.get_ts(),
            another_score.get_ts()
        )
        
        self.assertEqual(
            Score.identify(),
            b'Score'
        )
        
        self.assertEqual(
            score,
            Score.from_dict(**score.dict())
        )
        
        
   