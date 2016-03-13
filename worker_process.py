import multiprocessing


class WorkerProcess(multiprocessing.Process):
    def __init__(self, data, func, numworkers=None, chunksize=None):
        multiprocessing.Process.__init__(self)
        self.data = data
        self.func = func
        self.daemon = True
        self.pool = multiprocessing.Pool(numworkers)

    def run(self):
        return self.pool.map(self.func, self.data, chunksize=len(self.data)/multiprocessing.cpu_count()/8)