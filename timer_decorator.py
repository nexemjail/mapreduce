import time


def timer(f):
    def inner(*args, **kwargs):
        print('task', f.__name__ , 'started',)
        t = time.time()
        result = f(*args, **kwargs)
        print('task', f.__name__, 'took', (time.time() - t), 's')
        return result
    return inner