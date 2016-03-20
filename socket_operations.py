from __future__ import unicode_literals, print_function
import time
import threading
import logging


def get_local_port(host='localhost'):
    return host, 0


def configure_logging():
    logging.basicConfig(level=logging.DEBUG,
                        format='%(name)s: %(message)s'
                        )


def send_in_cycle(self, data_pickled):
    data_len = len(data_pickled)
    print('got : ' + str(data_len))
    sent_bytes = 0

    while sent_bytes < data_len:
        increment = self.send(data_pickled[sent_bytes:])
        if increment == 0:
            time.sleep(0.00)
        sent_bytes += increment

    print('sent : ' + str(sent_bytes))


def recv_data_into_array(self, input_data =list()):
    data = self.recv(self.chunk_size)
    while data:
        input_data.append(data)
        data = self.recv(self.chunk_size)
        time.sleep(0.01)
    return input_data


def send_in_thread(self, to_send):
    t = threading.Thread(target=send_in_cycle, args=(self, to_send))
    t.daemon = True
    t.start()
    #return t

