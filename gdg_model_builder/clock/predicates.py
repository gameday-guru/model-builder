import time
from datetime import datetime
from .clock import Predicate


# TODO: these need to be converted to tuple return types, one for the time of the event, one for the value used in cron serialization
async def poll(now : int):
    return int(time.time() * 1000)

def increment_factory(*, size_ns : int, name : int):
    last = None
    def _inner(count : int)->Predicate:
        async def _incr(now : int):
            nonlocal last
            now = int(now/size_ns) * (size_ns)
            if last is None or (now - last)/(1000 * 1000) > size_ns:
                last = now
                return now
            return -1
        _incr.__name__ = f"_{name}_{count}"
        return _incr
    return _inner

secs = increment_factory(size_ns=1000*1000, name="secs")
mins = increment_factory(size_ns=1000*1000*60, name="mins")
hours = increment_factory(size_ns=1000*1000*60*60, name="hours")
days = increment_factory(size_ns=1000*1000*1000*60*60*24, name="days")

def months(count : int)->Predicate:
    last = None
    async def _months(now : float):
        nonlocal last
        dt_now = datetime.fromtimestamp(now/(1000 * 1000))
        dt_last = datetime.fromtimestamp(now/(1000 * 1000))
        if last is None or (dt_now.month - dt_last.month) > count:
            return now
        return -1
    _months.__name__ = f"_months_{count}"
    return _months

def dow(which : int)->Predicate:
    last = None
    async def _dow(now : float):
        nonlocal last
        dt_now = datetime.fromtimestamp(now/(1000 * 1000))
        now_epoch_days = now/(1000 * 60 * 60 * 24)
        last_epoch_days = now/(1000 * 60 * 60 * 24)
        if dt_now.toordinal() % 7 == which and (last is None or now_epoch_days != last_epoch_days):
            return now
        return -1
    _dow.__name__ = f"_months_{which}"
    return _dow

def date_once(*, which : str, format : str)->Predicate:
    
    last = None
    async def _date_once(now : float):
        nonlocal last
        date_str = datetime.strftime(which, format)
        now_str = datetime.fromtimestamp(now/1000).strftime(format)
        if last is None and date_str == now_str:
            return now
        return -1
    _date_once.__name__ = f"_months_{which}_{format}"
    return _date_once