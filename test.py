from __future__ import print_function, generators
from mapreducetask import MapReduceTask
import multiprocessing
from worker import Worker
import timer_decorator
import time, datetime
import numpy as np


@timer_decorator.timer
def put_into(collection, input_queue):
    for el in collection:
        input_queue.put(el)
    print('completed')


@timer_decorator.timer
def make_test():
    collection = np.array(range(10**6))

    output_queue = multiprocessing.JoinableQueue()
    input_queue = multiprocessing.JoinableQueue()

    put_into(collection, input_queue)
    # processes = [multiprocessing.Process(target=put_into, args=(splitted_array[i], input_queue),)
    #              for i in range(multiprocessing.cpu_count())]
    # for p in processes:
    #     p.start()
    # for p in processes:
    #     p.join(3)
    #     p.terminate()
    #     print(p.exitcode)

    print('ended to put')
    print (input_queue.qsize())
    map_function = lambda x: (x,x)
    workers = [Worker(input_queue, output_queue, map_function, str(i)) for i in range(multiprocessing.cpu_count())]

    for w in workers:
        w.start()
        print(w.name, datetime.datetime.now())

    input_queue.join()

    processed_values_count = 0
    print('qsize', output_queue.qsize())
    while not output_queue.empty():
        processed_values_count += 1
        output_queue.get()
    print(processed_values_count)





if __name__ == '__main__':
    make_test()
    #mr = MapReduceTask()
    #print mr.execute(
    #    collection,
    #    lambda x: (x, x),
    #    lambda k, v: sum(v)
    #)