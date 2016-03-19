from __future__ import print_function
from __future__ import unicode_literals
from __future__ import generators
import multiprocessing
import collections
import itertools
import asyncore
from timer import timer
from client_server_intercommunication import Client, Server, WorkHandler, get_local_port, configure_logging
import numpy as np
from pickler import pickle_object, unpickle
import time
import threading
import Queue


class MapReduce(object):

    def __init__(self, map_function, reduce_funcion, local=True, num_workers=1):
        self.map_fuction = map_function
        self.reduce_function = reduce_funcion
        self.local = local
        self.num_workers = num_workers
        configure_logging()
        if local:
            self.pool = multiprocessing.Pool(self.num_workers)

    def partition(self, mapped_values):
        partitioned_data = collections.defaultdict(list)
        for key, value in mapped_values:
            partitioned_data[key].append(value)
        return partitioned_data.items()

    def mapping(self, inputs, chunksize = None):
        return self.pool.map(self.map_fuction, inputs, chunksize=chunksize)


    @staticmethod
    def _create_clients_and_workers(data_chunks, num_workers, function, addresses=get_local_port()):
        if addresses == get_local_port():
            addresses = [addresses] * num_workers
        workers = [Server(addresses[index], name='Server ' + str(index + 1)) for index in xrange(num_workers)]
        addresses = [worker.address for worker in workers]

        clients = []
        for i, (host, port) in enumerate(addresses):
            clients.append(Client(host,port,message=pickle_object((function, data_chunks[i])), name='Client ' + str(i+1)))

        return clients, workers


    @staticmethod
    def _check_done(clients):
        pass

    def _create_monitor_thread(self, clients):
        queue = Queue.Queue()
        t = threading.Thread(target=self.wait_data, args=(clients, queue))
        t.daemon = True
        t.start()
        return queue

    def _perform_mapping(self, inputs):
        data_chunks = np.array_split(inputs, self.num_workers)
        clients, workers = self._create_clients_and_workers(data_chunks,self.num_workers,self.map_fuction)

        queue = self._create_monitor_thread(clients)

        #for c in clients:
        #    c.terminate_task()

        asyncore.loop(use_poll=True, timeout=1)

        data = queue.get()
        array = np.array(data).reshape((-1,2))
        print(array)

        return array

    @staticmethod
    def _slice(inputs, num_slices):
        length = len(inputs)
        step = length / num_slices + 1
        current_position = 0
        parts = [] * num_slices
        while current_position <= length:
            parts.append(inputs[current_position:current_position + step])
            current_position += step
        return parts

    def _perform_reducing(self, inputs):
        data_chunks = self._slice(inputs,self.num_workers)
        clients, workers = self._create_clients_and_workers(data_chunks, self.num_workers, self.reduce_function)

        queue = self._create_monitor_thread(clients)

        asyncore.loop(use_poll=True, timeout=1)

        data = queue.get()
        raveled_data = []
        for el in data:
            raveled_data.extend(el)

        array = np.array(raveled_data).reshape((-1,2))

        return array

    def __call__(self, inputs, chunksize = None):
        assert isinstance(inputs, np.ndarray) is True
        if self.local:
            map_responses = self.mapping(inputs, chunksize)
            partitioned_data = self.partition(itertools.chain(map_responses))
            reduced_values = self.pool.map(self.reduce_function,
                                    partitioned_data)
            return reduced_values
        else:
            mapped_values = self._perform_mapping(inputs)
            partitioned_data = self.partition(itertools.chain(mapped_values))
            reduced_values = self._perform_reducing(partitioned_data)
            return reduced_values

    def wait_data(self, clients, queue):
        result_data = [None] * self.num_workers
        ready_flags = [False] * self.num_workers
        all_ready_flags = [True] * self.num_workers
        while True:
            time.sleep(0.5)
            for index in range(self.num_workers):
                if clients[index].ready() and  clients[index] is not None:
                    result_data[index] = clients[index].get()
                    ready_flags[index] = True
            if ready_flags == all_ready_flags:
                queue.put(result_data)
                break
        asyncore.close_all()




def map_function(x):
    return (x,1)


def reduce_function((k,v)):
    return (k, sum(v, 0))


if __name__ == '__main__':

    inputs = np.arange(start=0, stop=10**5/2, dtype=np.float32)
    mr = MapReduce(map_function = map_function,reduce_funcion=reduce_function, local=False, num_workers=4)
    result = mr(inputs)

    print(result)
    print(result.shape)


