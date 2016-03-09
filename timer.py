import time


def timer(foo):
    def inner(*args, **kwargs):
        t = time.time()
        result = foo(*args,**kwargs)
        print('time spent  for ' + foo.__name__, time.time() - t)
        return result
    return inner
cd  