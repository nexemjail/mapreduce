from mapreduce import MapReduce
import numpy as np
from timer import timer
from networks import Server, Client, get_local_port
import asyncore
import threading
from host_data import FAILED_MESSAGE
from pickler import pickle_object
def map_foo(x):
    return (x, 1)


def reduce_foo((x, y)):
    return (x, sum(y))


@timer
def test(collection):
    mr = MapReduce(map_foo, reduce_foo,local=False,num_workers=2)
    return mr(collection)


def test_client(host, port, message):
    c = Client(host,port,message)
    asyncore.loop(use_poll=True, timeout=0.5)

if __name__ == '__main__':

    host, port = get_local_port()
    server = Server((host,port))
    host, port = server.address

    t = threading.Thread(target=test_client, args =(host,port,pickle_object((map_foo,[range(50)]))))
    t.daemon = True
    t.start()

    asyncore.loop(use_poll=True, timeout=1)


    #collection_length = 10 ** 5
    #collection = np.random.random_integers(0, collection_length/15, collection_length)
    #result = test(collection)
    #print result
