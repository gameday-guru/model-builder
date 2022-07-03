import unittest
import time
from fastapi import FastAPI
from libutil.sync.deasync import deasync

def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            print('%r  %2.2f ms' % (method.__name__, (te - ts) * 1000))
        return result
    return timed
 
class MYTestCase(unittest.TestCase):
    """Checks that the get_image_colors methods work appropriately.
    """

    @deasync
    async def test_can_create_callable(self):
        """Experimenting with fast api
        """
        app = FastAPI()
        async def add(a : int, b : int)->int:
            return a + b

        @app.post(add.__name__)
        async def inner(a : int, b : int)->int:
            return a + b
    