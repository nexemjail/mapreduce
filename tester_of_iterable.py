from mapreduce import MapReduce
import numpy as np
from timer import timer


def map_foo(x):
    return (x, 1)


def reduce_foo((x, y)):
    return (x, sum(y))


@timer
def test(collection):
    mr = MapReduce(map_foo, reduce_foo)
    return mr(collection, chunksize = len(collection) / 40)

if __name__ == '__main__'   :
    #collection = range(10**5)
    collection_length = 10 ** 6
    collection = np.random.random_integers(0, collection_length/15, collection_length)
    result = test(collection)