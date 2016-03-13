import numpy as np


class Worker(object):
    def __init__(self, func):
        self.func = func

    def __call__(self, data):

        if isinstance(data, np.ndarray):
            vectorized_func = np.vectorize(self.func)
            return vectorized_func(data)
        else:
            data = list(data)
            return map(self.func, data)
