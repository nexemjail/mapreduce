from __future__ import print_function, unicode_literals
import asyncore
import logging
import socket
import time
from pickler import pickle_object, unpickle
from host_data import HOST, TERMINATE_MESSAGE, PORT, FAILED_MESSAGE, BUFFER_SIZE
from serve_in_process import create_server, create_and_get_address
from socket_operations import send_in_cycle, get_local_port, configure_logging, recv_data_into_array


class Client(asyncore.dispatcher):
    """Sends messages to the server and receives responses.
    """

    def __init__(self, host, port, message = None, chunk_size=BUFFER_SIZE, name = 'Client'):
        asyncore.dispatcher.__init__(self)

        self.message_query = []
        if message:
            self.message_query.append(message)
        self.chunk_size = chunk_size
        self.logger = logging.getLogger(name)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)

        # self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF,10**9)
        # self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF,10**9)

        self.logger.debug('connecting to %s', (host, port))
        self.connect((host, port))
        self.data = None
        self.is_ready = True

    def handle_connect(self):
        self.logger.debug('handle_connect()')

    def handle_close(self):
        self.logger.debug('handle_close()')
        self.close()

    def writable(self):
        is_writable = bool(self.message_query)
        self.logger.debug('writable() -> %s', is_writable)
        return is_writable

    def handle_write(self):
        to_send, self.message_query = self.message_query[0], self.message_query[1:]
        send_in_cycle(self,to_send)
        #_send_in_cycle(self, to_send)

    def handle_read(self):
        input_data = []
        try:
            input_data = recv_data_into_array(self, input_data)
        except socket.error:
            #here got eof and an error. Don't know, why?
            pass
        all_data = ''.join(input_data)
        print('got in client : ' + str(len(all_data)))
        try:
            data = unpickle(all_data)
            self.data = data
        except EOFError:
            #stackoverflow says that it is normal
            self.logger.debug('Unexpected EOF!')
            pass

        if self.data == FAILED_MESSAGE:
            self.logger.debug(FAILED_MESSAGE)
        else:
            self.logger.debug('handle_read()  i ve got what you wanted!')
        #    self.logger.debug('handle_read() "%s"',str(data))

    def send_message(self, message):
        self.message_query.append(message)

    # def handle_error(self):
    #     self.logger.debug('Error ocured!')

    def terminate_task(self):
        self.message_query.append(TERMINATE_MESSAGE)

    def ready(self):
        self.is_ready = self.data is not None
        return self.is_ready

    def get(self):
        if self.is_ready:
            self.is_ready = False
            return self.data


def map_function(x):
    return (x,1)


def term(server_process):
    time.sleep(10)
    server_process.terminate()


def create_client(host = None, port = None):
    configure_logging()
    if host is not None and port is not None:
        host, port = create_and_get_address()

    #inputs = np.arange(10**6)
    client = Client(host, port)

    #t = threading.Thread(target=term, args=(server_process,))
    #t.start()
    asyncore.loop(use_poll=True, timeout=1)


if __name__ == '__main__':
    create_client()
