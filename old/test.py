from __future__ import print_function, generators

import multiprocessing

import numpy as np
from worker import Worker

from old import timer_decorator


@timer_decorator.timer
def put_into(collection, input_queue, num_q = multiprocessing.cpu_count()):
    for el in collection:
        input_queue.put(el)
    for i in range(num_q):
        input_queue.put(None)
    input_queue.cancel_join_thread()


@timer_decorator.timer
def put_into_for_single_queue(collection, input_queue):
    for el in collection:
        input_queue.put(el)
    input_queue.put(None)
    input_queue.cancel_join_thread()



@timer_decorator.timer
def make_test():
    num_queues = multiprocessing.cpu_count()
    collection = np.array(range(100))

    #manager = multiprocessing.Manager()

    output_queue = multiprocessing.Queue()

    output_queues = [multiprocessing.JoinableQueue() for _ in range(num_queues)]
    input_queues = [multiprocessing.JoinableQueue() for _ in range(num_queues)]

    splitted_array = np.array_split(collection,multiprocessing.cpu_count())
    processes = [multiprocessing.Process(target=put_into_for_single_queue,
                                         args=(splitted_array[i], input_queues[i]),)
                  for i in range(num_queues)]
    for p in processes:
        p.start()

    for p in processes:
        p.join()
    print('joined!')

    for q in input_queues:
        print(q.qsize()),

    map_function = lambda x: (x,x)

    workers = [Worker(input_queues[i],output_queue, map_function) for i in range(num_queues)]

    for w in workers:
        p.daemon = True
        print('started ' + p.name)
        w.start()

    for w in workers:
        w.join()
    for q in output_queues:
        print(q.qsize()),

    print('joined!')
    processed_values_count = 0
    results = []
    for i in range(len(workers)):
        while not output_queues[i].empty():
            processed_values_count += 1
            results.append(output_queues[i].get_result())
    print('len', len(results))





if __name__ == '__main__':
    make_test()
    #mr = MapReduceTask()
    #print mr.execute(
    #    collection,
    #    lambda x: (x, x),
    #    lambda k, v: sum(v)
    #)