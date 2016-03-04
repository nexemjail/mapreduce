import multiprocessing
from timer_decorator import timer
import numpy as np
from worker import Worker

@timer
def fill_queue(queue, values):
    for v in values:
        queue.put(v)
    queue.put(None)
    queue.cancel_join_thread()


if __name__ == "__main__":


    manager = multiprocessing.Manager()
    managers_dict = manager.dict()


    collection_size = 500
    num_processes = multiprocessing.cpu_count()

    output_queue = multiprocessing.JoinableQueue()
    subarrays = np.array_split(np.random.random_integers(0,500,collection_size),num_processes)


    input_queues = []
    output_queues = []
    for _ in range(num_processes):
        iq = multiprocessing.JoinableQueue()
        oq = multiprocessing.JoinableQueue()
        input_queues.append(iq)
        output_queues.append(oq)


    fillers = []
    for i in range(num_processes):
        p = multiprocessing.Process(target=fill_queue,name='filler ' + str(i),
                                    args=(input_queues[i], subarrays[i]))
        p.start()
        fillers.append(p)

    for filler in fillers:
        filler.join()

    print('filled queues')

    for q in input_queues:
        print(q.qsize())

    map_function = lambda x: (x,x)

    workers = [] * num_processes
    for i in range(num_processes):
        worker = Worker(input_queues[i], output_queue=output_queues[i], map_function=map_function)
        worker.start()

    for q in input_queues:

        q.join()







