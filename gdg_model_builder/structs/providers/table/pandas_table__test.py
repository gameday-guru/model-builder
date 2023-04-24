import unittest
from .table import PandasTable
import redis
from gdg_model_builder.structs.providers.model_struct import ModelStruct
import json
from gdg_model_builder.serializer.providers.redis.redis_model_serializer import RedisModelSerializer

class TestPandasTable(unittest.TestCase):
    
    store : redis.Redis = redis.Redis(db=0)
    
    class ModelSerializer(RedisModelSerializer[str, ModelStruct]):
        
        model : ModelStruct
        
        def __init__(self, *args, store: redis.Redis, model_name: str, state_name: str, model : type[ModelStruct]) -> None:
            super().__init__(*args, store=store, model_name=model_name, state_name=state_name)
            self.model = model
        
        def deserialize(self, value: bytes) -> ModelStruct:
            return self.model.parse_obj(
                json.loads(str(value, encoding=self.encoding))
            )
        
        def serialize(self, value: ModelStruct) -> bytes:
            return bytes(
                json.dumps(value.dict()), 
                encoding=self.encoding
            )
        
        def hash(self, key: str) -> bytes:
            return bytes(key, encoding=self.encoding)
        
        def unhash(self, key: bytes) -> str:
            return str(key, encoding=self.encoding) 
   
    def test_pandas_table(self):
        
        class Model(ModelStruct):
            f : str
            t : str
        
        s = self.ModelSerializer(
            store=self.store,
            model_name="RedisModelSerializerTest",
            state_name="test_pandas_table",
            model=Model
        )
        s.empty()
        
        t = PandasTable(serializer=s)
        
        t["a"] = Model(t="Liam", f="Kayla")
        t["b"] = Model(t="Liam", f="Kayla")
        t["c"] = Model(t="Kayla", f="Liam")
        model_df = t.frame
        to_liam = model_df[model_df["t"] == "Liam"]
        self.assertEqual(list(to_liam["t"]), ["Liam", "Liam"])
        
    def test_pandas_table_struct_hash(self):
        
        class Model(ModelStruct):
            f : str
            t : str
        
        s = self.ModelSerializer(
            store=self.store,
            model_name="TableTest",
            state_name="test_pandas_table_struct_hash",
            model=Model
        )
        s.empty()
        
        t = PandasTable(serializer=s)
        
        t["a"] = Model(t="Liam", f="Kayla")
        t["b"] = Model(t="Liam", f="Kayla")
        t["c"] = Model(t="Kayla", f="Liam")
        
        self.assertEqual(t.struct_hash(), t.struct_hash())
        
        residual = t.struct_hash()
        t["d"] = Model(t="Liam", f="Kayla")
        self.assertNotEqual(residual, t.struct_hash())
        
    def test_big_pandas_table_struct_hash(self):
        
        class Model(ModelStruct):
            f : str
            t : str
        
        s = self.ModelSerializer(
            store=self.store,
            model_name="TableTest",
            state_name="test_big_table_too",
            model=Model
        )
        s.empty()
        
        t = PandasTable(serializer=s)
        
        print("available")
        for i in range(0, 1_000):
            print("writing")
            t[f"{i}"] = Model(t="Liam", f="Kayla")
            
        print("wrote")
        
        self.assertEqual(t.struct_hash(), t.struct_hash())
        
        residual = t.struct_hash()
        t["d"] = Model(t="Liam", f="Kayla")
        self.assertNotEqual(residual, t.struct_hash())
        
        
        