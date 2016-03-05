from __future__ import print_function
from __future__ import unicode_literals
from __future__ import generators
import multiprocessing
import collections
import itertools


class MapReduce(object):

    def __init__(self, map_function, reduce_funcion, num_workers = None):
        self.map_fuction = map_function
        self.reduce_function =  reduce_funcion
        self.pool = multiprocessing.Pool(num_workers)

    def partition(self, mapped_values):
        partitioned_data = collections.defaultdict(list)
        for key, value in mapped_values:
            partitioned_data[key].append(value)
        return partitioned_data.iteritems()

    def __call__(self, inputs, chunksize = 1):
        map_responses = self.pool.map(self.map_fuction, inputs, chunksize=chunksize)
        partitioned_data = self.partition(itertools.chain(map_responses))
        reduced_values = self.pool.map(self.reduce_function, partitioned_data)
        return reduced_values









print(sorted([el for el in dir(multiprocessing.JoinableQueue()) if not el.startswith('_')]))