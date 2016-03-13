import socket

from host_data import HOST, PORT,TERMINATE_MESSAGE
from pickler import pickle_object
from workers.combiner import Combiner
from workers.worker import Worker
import time


def send_to(data, host=HOST, port=PORT):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    client_socket.send(data)
    time.sleep(5)
    #client_socket.close()


def send_data(data):
    send_to(data)
    return True

map_func = lambda x: (x,1)
def reduce_func((k,v)):
    return (k, sum(v))

if __name__ == '__main__':
    # mapper = Worker(map_func)
    # reducer = Worker(reduce_func)
    # combiner = Combiner()

    # data = range(1000) * 15
    #
    # mapped_values = mapper(data)
    # combined_values = combiner(mapped_values)
    # reduced_values = reducer(combined_values)
    # print reduced_values

    send_data(pickle_object((reduce_func, [(1, [123])])))
    #send_data(TERMINATE_MESSAGE)
