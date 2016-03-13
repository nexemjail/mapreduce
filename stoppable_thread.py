import threading
from multiprocessing import Pool


class StoppableThread(threading.Thread):
    def __init__(self, function, data, processes = None):
        threading.Thread.__init__(self)
        self._stop_event = threading.Event()
        self._sleep_period = 0.05
        self.function = function
        self.data = data
        self.pool = Pool(processes=processes)
        self.terminated = False
        self.result = None
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    
    def run(self):
        result = self.pool.map_async(self.function, self.data,chunksize=len(self.data)/40 + 1)
        while not self._stop_event.isSet() and  not result.ready():
            self._stop_event.wait(timeout=self._sleep_period)
        if result.ready():
            self.result = result.get()
        if self._stop_event.isSet():
            self.pool.terminate()
            self.pool.join()
            return

    def get(self):
        if self.result:
            return self.result
        return None

    def ready(self):
        return bool(self.result)

    def terminate(self):
        self._stop_event.set()
