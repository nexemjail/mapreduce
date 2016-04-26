from __future__ import print_function
from __future__ import unicode_literals
from __future__ import generators
import multiprocessing
import collections
import itertools
import asyncore
from timer import timer
from networks import Client, Server, get_local_port, configure_logging
import numpy as np
from pickler import pickle_object, unpickle
import time
import threading

try:
    from queue import Queue
except ImportError:
    from Queue import Queue


def split(a, n):
    k, m = len(a) / n, len(a) % n
    return (a[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in xrange(n))


def ravel_array(array):
    raveled_array = []
    for subarray in array:
        raveled_array.extend(subarray)
    return raveled_array


class MapReduce(object):

    def __init__(self, map_function, reduce_function, local=True, num_workers=1):
        self.map_function = map_function
        self.reduce_function = reduce_function
        self.local = local
        self.num_workers = num_workers
        configure_logging()
        if local:
            self.pool = multiprocessing.Pool(self.num_workers)

    @staticmethod
    def partition(mapped_values):
        partitioned_data = collections.defaultdict(list)
        for key, value in mapped_values:
            partitioned_data[key].append(value)
        return partitioned_data.items()

    def mapping(self, inputs, chunksize=None):
        return self.pool.map(self.map_function, inputs, chunksize=chunksize)

    @staticmethod
    def _create_clients_and_workers(data_chunks, num_workers, function, addresses=get_local_port()):
        if addresses == get_local_port():
            addresses = [addresses] * num_workers
        workers = [Server(addresses[index], name='Server ' + str(index + 1)) for index in range(num_workers)]
        addresses = [worker.address for worker in workers]

        clients = []
        for i, (host, port) in enumerate(addresses):
            clients.append(Client(host,port,message=pickle_object((function, data_chunks[i])), name='Client ' + str(i+1)))

        return clients, workers

    def _create_monitor_thread(self, clients):
        queue = Queue()
        t = threading.Thread(target=self._wait_data, args=(clients, queue))
        t.daemon = True
        t.start()
        return queue

    def _perform_mapping(self, inputs):
        data_chunks = list(split(inputs, self.num_workers))
        clients, workers = self._create_clients_and_workers(data_chunks, self.num_workers, self.map_function)

        queue = self._create_monitor_thread(clients)

        asyncore.loop(use_poll=True, timeout=0.3)

        data = queue.get()

        return data

    def _perform_reducing(self, inputs):
        data_chunks = list(split(inputs,self.num_workers))
        clients, workers = self._create_clients_and_workers(data_chunks, self.num_workers, self.reduce_function)

        queue = self._create_monitor_thread(clients)

        asyncore.loop(use_poll=True, timeout=0.3)

        data = queue.get()

        return data

    def __call__(self, inputs, chunksize = None):
        if self.local:
            map_responses = self.mapping(inputs, chunksize)
            partitioned_data = self.partition(itertools.chain(map_responses))
            reduced_values = self.pool.map(self.reduce_function,
                                    partitioned_data)
        else:
            mapped_values = self._perform_mapping(inputs)
            partitioned_data = self.partition(itertools.chain(mapped_values))
            reduced_values = self._perform_reducing(partitioned_data)
        return reduced_values

    def _wait_data(self, clients, queue):
        result_data = [None] * self.num_workers
        ready_flags = [False] * self.num_workers
        all_ready_flags = [True] * self.num_workers
        while True:
            time.sleep(0.2)
            for index in range(self.num_workers):
                if clients[index].ready() and clients[index] is not None:
                    result_data[index] = clients[index].get()
                    ready_flags[index] = True
            if ready_flags == all_ready_flags:
                raveled_data = ravel_array(result_data)
                queue.put(raveled_data)
                break
        asyncore.close_all()


def map_function(x):
    return (x,1)


def reduce_function(tup):
    return (tup[0], sum(tup[1], 0))


if __name__ == '__main__':

    collection_length = 10**5
    collection = list(np.random.random_integers(0, collection_length/15, collection_length))

    @timer
    def foo():
        mr = MapReduce(map_function=map_function, reduce_function=reduce_function, local=False, num_workers=2)
        result = mr(collection)

        print(result)

    foo()
