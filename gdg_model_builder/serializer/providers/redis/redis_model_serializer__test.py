import unittest
from .redis_model_serializer import RedisModelSerializer
import redis
from gdg_model_builder.structs.providers.model_struct.model_struct import ModelStruct
import json

class RedisModelSerializerTest(unittest.TestCase):
    """Checks that the get_image_colors methods work appropriately.
    """
    
    class StrSerializer(RedisModelSerializer[str, str]):
        
        def deserialize_element(self, value: bytes) -> str:
            return str(value, encoding=self.encoding)
        
        def serialize_element(self, value: str) -> bytes:
            return bytes(value, encoding=self.encoding)
        
        def hash(self, key: str) -> bytes:
            return bytes(key, encoding=self.encoding)
        
        def unhash(self, key: bytes) -> str:
            return str(key, encoding=self.encoding)
    
    class ModelSerializer(RedisModelSerializer[str, ModelStruct]):
        
        model : ModelStruct
        
        def __init__(self, *args, store: redis.Redis, model_name: str, state_name: str, model : type[ModelStruct]) -> None:
            super().__init__(*args, store=store, model_name=model_name, state_name=state_name)
            self.model = model
        
        def deserialize_element(self, value: bytes) -> ModelStruct:
            return self.model.parse_obj(
                json.loads(str(value, encoding=self.encoding))
            )
        
        def serialize_element(self, value: ModelStruct) -> bytes:
            return bytes(
                json.dumps(value.dict()), 
                encoding=self.encoding
            )
        
        def hash(self, key: str) -> bytes:
            return bytes(key, encoding=self.encoding)
        
        def unhash(self, key: bytes) -> str:
            return str(key, encoding=self.encoding)
    
    store : redis.Redis = redis.Redis(db=0)

    def test_sets_and_gets(self):
        
        s = self.StrSerializer(
            store=self.store,
            model_name="RedisModelSerializerTest",
            state_name="test_sets_and_gets"
        )
        s.empty()
        
        bench_a = "aardvark"
        s["a"] = bench_a
        res_a = s["a"]
        self.assertAlmostEquals(bench_a, res_a)
        
        s.empty()
        res_a = s["a"]
        self.assertIsNone(res_a)
        
    def test_values(self):
        
        s = self.StrSerializer(
            store=self.store,
            model_name="RedisModelSerializerTest",
            state_name="test_values"
        )
        s.empty()
        
        bench_a = "aardvark"
        bench_b = "banana"
        bench_d = "dales"
        s["a"] = bench_a
        s["b"] = bench_b
        s["d"] = bench_d
        
        bench_list_pre = [bench_a, bench_b, bench_d]
        self.assertListEqual(list(s.values()), bench_list_pre)
        
        bench_c = "coral"
        s["c"] = bench_c
        
        bench_list_coral = [bench_a, bench_b, bench_c, bench_d]
        self.assertListEqual(list(s.values()), bench_list_coral)
        
        del s["b"]
        bench_list_bye_b = [bench_a, bench_c, bench_d]
        self.assertListEqual(list(s.values()), bench_list_bye_b)
        
        s.empty()
        res_a = s["a"]
        self.assertIsNone(res_a)
        
    def test_values(self):
        
        s = self.StrSerializer(
            store=self.store,
            model_name="RedisModelSerializerTest",
            state_name="test_values"
        )
        s.empty()
        
        bench_a = "aardvark"
        bench_b = "banana"
        bench_d = "dales"
        s["a"] = bench_a
        s["b"] = bench_b
        s["d"] = bench_d
        
        bench_list_pre = [bench_a, bench_b, bench_d]
        self.assertListEqual(list(s.values()), bench_list_pre)
        
        bench_c = "coral"
        s["c"] = bench_c
        
        bench_list_coral = [bench_a, bench_b, bench_c, bench_d]
        self.assertListEqual(list(s.values()), bench_list_coral)
        
        del s["b"]
        bench_list_bye_b = [bench_a, bench_c, bench_d]
        self.assertListEqual(list(s.values()), bench_list_bye_b)
        
        s.empty()
        res_a = s["a"]
        self.assertIsNone(res_a)
        
    def test_values(self):
        
        s = self.StrSerializer(
            store=self.store,
            model_name="RedisModelSerializerTest",
            state_name="test_values"
        )
        s.empty()
        
        bench_a = "aardvark"
        bench_b = "banana"
        bench_d = "dales"
        s["a"] = bench_a
        s["b"] = bench_b
        s["d"] = bench_d
        
        bench_list_pre = [bench_a, bench_b, bench_d]
        self.assertListEqual(list(s.values()), bench_list_pre)
        
        bench_c = "coral"
        s["c"] = bench_c
        
        bench_list_coral = [bench_a, bench_b, bench_c, bench_d]
        self.assertListEqual(list(s.values()), bench_list_coral)
        
        del s["b"]
        bench_list_bye_b = [bench_a, bench_c, bench_d]
        self.assertListEqual(list(s.values()), bench_list_bye_b)
        
        s.empty()
        res_a = s["a"]
        self.assertIsNone(res_a)
        
    def test_base_modeler(self):
        
        class Model(ModelStruct):
            f : str
            t : str
        
        s = self.ModelSerializer(
            store=self.store,
            model_name="RedisModelSerializerTest",
            state_name="test_values_base_model",
            model=Model
        )
        s.empty()
        
        bench_a = Model(
            f="liam",
            t="kayla"
        )
        s["a"] = bench_a
        print(s["a"])
        # s["b"] = bench_b
        # s["d"] = bench_d
        
        
        