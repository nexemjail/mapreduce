from __future__ import print_function

import multiprocessing
import time
from collections import defaultdict


class Worker(multiprocessing.Process):
    def __init__(self, input_queue, output_queue, manager, map_function):
        multiprocessing.Process.__init__(self)
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.manager = manager
        self.map_function = map_function

    def run(self):
        time.sleep(0.001)
        #times_got = 0
        dict_ = self.manager.dict()
        dict_ = defaultdict(list)

        while True:
            value = self.input_queue.get_nowait()
            #times_got += 1
            #if value % 50 == 0:
            #print(value)
            if value is None:
                self.input_queue.task_done()
                #self.output_queue.cancel_join_thread()
                print('------------finished')
                self.output_queue.put(dict_, False)
                self.output_queue.cancel_join_thread()
                self.output_queue.close()
                break
            key, val = self.map_function(value)
            #dict_.setdefault(key, [])
            dict_[key].append(val)

            #self.output_queue.put(self.map_function(value))
            print(self.input_queue.qsize(), multiprocessing.current_process().name)
            self.input_queue.task_done()







