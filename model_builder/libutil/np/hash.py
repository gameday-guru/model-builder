import hashlib
import numpy as np

def hasharr(arr : np.ndarray)->bytes:
    """Hashes a numpy array.

    :param arr: _description_
    :type arr: np.ndarray
    :return: _description_
    :rtype: bytes
    """

    hash = hashlib.sha256(arr.tobytes())
    for dim in arr.shape:
        hash.update(dim.to_bytes(4, byteorder='big'))
    return hash.digest()