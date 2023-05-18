import unittest
from gdg_model_builder.util.deasync import deasync
from .redis_collection import RedisCollection
from gdg_model_builder.shape import PydanticShape

class Score(PydanticShape):
    home : int
    away : int

class ScoreCollection(RedisCollection): shape = Score

class RedisCollectionTest(unittest.TestCase):
    
    @deasync
    async def test_redis_collection(self):
        collection = ScoreCollection(
            name="test",
        )
        collection["first"] = Score(
            home=1,
            away=2
        )
        await collection.commit()
        new_collection = ScoreCollection(name="test")
        self.assertEqual(
            collection["first"],
            new_collection["first"]
        )
    