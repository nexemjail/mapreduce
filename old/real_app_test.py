from __future__ import generators
from __future__ import print_function

import multiprocessing
from multiprocessing.queues import Full

import numpy as np
from custom_queue import DickQueue as Dick
from worker import Worker


def fill_queue(queue, values):
    for v in values:
        try:
            queue.put(v, False)
        except Full:
            queue.flush()
    queue.put_nowait(None)
    queue.cancel_join_thread()

if __name__ == "__main__":

    manager = multiprocessing.Manager()

    collection_size = 10**7
    num_processes = multiprocessing.cpu_count()

    output_queue = Dick(ctx=multiprocessing.get_context(),maxsize=10**8)
    subarrays = np.array_split(np.random.random_integers(0,10,collection_size),num_processes)


    input_queues = []
    output_queues = []
    for _ in range(num_processes):
        iq = Dick(ctx=multiprocessing.get_context(), maxsize=10**8)
        oq = Dick(ctx=multiprocessing.get_context(), maxsize=10**8)
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

    # for q in input_queues:
    #     print(q.qsize())

    map_function = lambda x: (x,x)

    workers = []
    for i in range(num_processes):
        worker = Worker(input_queues[i], output_queue=output_queue, manager=manager,map_function=map_function)
        worker.start()
        workers.append(worker)

    # for iq in input_queues:
    #     iq.join()
    #
    for w in workers:
        w.join()

    # for q in :
    #     print (q.qsize()),
    # print('mamka')

    dicts = []
    for i in range(num_processes):
        dicts.append(output_queue.get())
        print(dicts[i])

    #for key in managers_dict.keys():
    #    print(managers_dict[key])
    #print(output_queue.qsize())





