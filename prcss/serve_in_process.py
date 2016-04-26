from __future__ import print_function
from __future__ import unicode_literals
import asyncore
import logging
import stoppable_thread
import socket
import threading
import time
from pickler import pickle_object, unpickle
from host_data import HOST, TERMINATE_MESSAGE, PORT, FAILED_MESSAGE, BUFFER_SIZE
import multiprocessing
from socket_operations import send_in_cycle, get_local_port, configure_logging, recv_data_into_array


class Server(asyncore.dispatcher):
    """
        Receives connections and establishes handlers for each client.
    """
    def __init__(self, address, name = 'Server'):
        asyncore.dispatcher.__init__(self)
        self.logger = logging.getLogger(name)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF,10**9)
        # self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF,10**9)

        self.bind(address)
        self.address = self.socket.getsockname()
        self.logger.debug('binding to %s', self.address)
        self.listen(5)

    def handle_accept(self):
        # Called when a client connects to our socket
        client_info = self.accept()
        self.logger.debug('handle_accept() -> %s', client_info[1])
        WorkHandler(sock=client_info[0])
        # We only want to deal with one client at a time,
        # so close as soon as we set up the handler.
        # Normally you would not do this and the server
        # would run forever or until it received instructions
        # to stop.

        self.handle_close()

    def handle_close(self):
        self.logger.debug('handle_close()')
        self.close()


class WorkHandler(asyncore.dispatcher):
    """
        Handles echoing messages from a single client.
    """

    def __init__(self, sock, chunk_size=BUFFER_SIZE):
        asyncore.dispatcher.__init__(self, sock=sock)
        self.chunk_size = chunk_size
        self.logger = logging.getLogger('WorkHandler%s' % str(sock.getsockname()))
        self.task = None
        self.terminated = False
        return

    def writable(self):
        """We want to write if we have received data."""

        if self.terminated:
            #when we are terminated, send a response with info that we are hyperdone!
            response_ready = True
        else:
            response_ready = bool(self.task and self.task.ready())
        self.logger.debug('writable() -> %s', response_ready)
        return response_ready

    def handle_write(self):
        """Write as much as possible of the most recent message we have received."""
        if not self.terminated:
            raw_data = self.task.get_result()
        else:
            raw_data = [FAILED_MESSAGE]

        data_pickled = pickle_object(raw_data)

        send_in_cycle(self, data_pickled)
        self.task = None
        self.terminated = False
        if not self.writable():
            self.handle_close()

    def handle_read(self):
        input_data = []
        data = self.recv(self.chunk_size)
        if data == TERMINATE_MESSAGE:
            if self.task and not self.task.ready():
                self.task.terminate()
                self.logger.debug('task terminated!')
                self.terminated = True
        else:
            try:
                input_data.append(data)
                recv_data_into_array(self, input_data)
            except socket.error:
                pass
            all_data = ''.join(input_data)
            function, data = unpickle(all_data)
            self.task = stoppable_thread.StoppableThread(function, data)
            self.task.setDaemon(True)
            self.task.start()

        """Read an incoming message from the client and put it into our outgoing queue."""
        self.logger.debug('handle_read() -> (%d)', len(data))
        #self.result = all_data

    def handle_close(self):
        if self.task is not None:
            self.task.terminate()
        self.logger.debug('handle_close()')
        self.close()

    #def handle_error(self):
    #    self.logger.debug('error occured!')


def runserver(queue,address, name='Server'):
    server = Server(address=address, name=name)
    queue.put(server.address)
    asyncore.loop(timeout=1, use_poll=True)


def create_server(address = get_local_port(), name='Server'):
    configure_logging()
    queue = multiprocessing.Queue()

    process = multiprocessing.Process(target=runserver,args=(queue,address, name))
    process.start()
    return process, queue


def create_and_get_address(address = get_local_port(), name = 'Server'):
    process, queue = create_server(address, name)
    return queue.get()

if __name__ == '__main__':
    configure_logging()
    process, queue = create_server()

    address = queue.get()
    time.sleep(5)
    process.terminate()






