from mapreduce import MapReduce
import numpy as np
import time

def map_foo(x):
    return (x,1)


def reduce_foo((x,y)):
    return (x, sum(y))


def timer(foo):
    def inner(*args, **kwargs):
        t = time.time()
        result = foo(*args,**kwargs)
        print('time spent ', time.time() - t)
        return result
    return inner

@timer
def test(collection):
    mr = MapReduce(map_foo, reduce_foo)
    print(len(mr(collection)))

if __name__ == '__main__':
    #collection = range(10**5)
    collection_length = 10 ** 7
    collection = np.random.random_integers(0, collection_length, collection_length)
    test(collection)

    collection = xrange(collection_length)
    test(collection)