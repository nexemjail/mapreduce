from __future__ import print_function
import multiprocessing

class Worker(multiprocessing.Process):
    def __init__(self, input_queue, output_queue, map_function, name = 'worker'):
        multiprocessing.Process.__init__(self)
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.map_function = map_function
        self.name = name


    def run(self):
        while not self.input_queue.empty():
            value = self.input_queue.get()
            self.output_queue.put(self.map_function(value))
            self.input_queue.task_done()
            if self.input_queue.qsize() % 5000 == 0:
                print(self.name)



