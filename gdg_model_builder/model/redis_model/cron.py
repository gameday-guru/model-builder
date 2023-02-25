import time
from datetime import datetime
from ..modellike import LA


# TODO: these need to be converted to tuple return types, one for the time of the event, one for the value used in cron serialization
def poll(now : float, last : float):
    return float(time.time())

def secs(count : int)->LA:
    def _secs(now : float, last : float):
        if last is None or (now - last)/1000 > count:
            return now
        return -1
    _secs.__name__ = f"_secs_{count}"
    return _secs

def mins(count : int)->LA:
    def _mins(now : float, last : float):
        if last is None or (now - last)/(1000 * 60) > count:
            return now
        return -1
    _mins.__name__ = f"_mins_{count}"
    return _mins

def hours(count : int)->LA:
    def _hours(now : float, last : float):
        if last is None or (now - last)/(1000 * 60 * 60) > count:
            return now
        return -1
    _hours.__name__ = f"_hours_{count}"
    return _hours

def days(count : int, at : int = 0)->LA:
    def _days(now : float, last : float):
        last_floor = int((last or 0)/(1000 * 60 * 60 * 24)) * (1000 * 60 * 60 * 24) + at
        if last is None or (now - last_floor)/(1000 * 60 * 60 * 24) > count:
            return now
        return -1
    _days.__name__ = f"_days_{count}"
    return _days

def months(count : int)->LA:
    def _months(now : float, last : float):
        dt_now = datetime.fromtimestamp(now/1000)
        dt_last = datetime.fromtimestamp(last/1000)
        if last is None or (dt_now.month - dt_last.month) > count:
            return now
        return -1
    _months.__name__ = f"_months_{count}"
    return _months

def dow(which : int)->LA:
    def _dow(now : float, last : float):
        dt_now = datetime.fromtimestamp(now/1000)
        now_epoch_days = now/(1000 * 60 * 60 * 24)
        last_epoch_days = now/(1000 * 60 * 60 * 24)
        if dt_now.toordinal() % 7 == which and (last is None or now_epoch_days != last_epoch_days):
            return now
        return -1
    _dow.__name__ = f"_months_{which}"
    return _dow

def date_once(*, which : str, format : str)->LA:
    def _date_once(now : float, last : float):
        date_str = datetime.strftime(which, format)
        now_epoch_days = now/(1000 * 60 * 60 * 24)
        now_str = datetime.fromtimestamp(now/1000).strftime(format)
        if last is None and date_str == now_str:
            return now
        return -1
    _date_once.__name__ = f"_months_{which}_{format}"
    return _date_once