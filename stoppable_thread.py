import threading
from multiprocessing import Pool

class StoppableThread(threading.Thread):
    def __init__(self, function, data,processes = None):
        threading.Thread.__init__(self)
        self._stop_event = threading.Event()
        self._sleep_period = 0.2
        self.function = function
        self.data = data
        self.pool = Pool(processes=processes)

    def run(self):
        count = 0
        self.pool.map_async(self.function, self.data,chunksize=len(self.data)/40 + 1)
        while not self._stop_event.isSet() or self.pool.:
            self._stop_event.wait(self._sleep_period)

    def join(self, timeout=None):
        self._stop_event.set()
        threading.Thread.join(self, timeout)
