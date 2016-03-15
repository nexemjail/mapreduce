import asyncore
import logging
import stoppable_thread
import socket
import threading
import time
from pickler import pickle_object, unpickle
from host_data import HOST, TERMINATE_MESSAGE, PORT, FAILED_MESSAGE

BUFFER_SIZE = 8192


class Server(asyncore.dispatcher):
    """
        Receives connections and establishes handlers for each client.
    """

    def __init__(self, address):
        asyncore.dispatcher.__init__(self)
        self.logger = logging.getLogger('Server')
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
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
            raw_data = FAILED_MESSAGE

        data_pickled = pickle_object(raw_data)
        _ = self.sendall(data_pickled)
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
                while data:
                    input_data.append(data)
                    data = self.recv(self.chunk_size)
            except socket.error:
                pass
            all_data = ''.join(input_data)
            function, data = unpickle(all_data)
            self.task = stoppable_thread.StoppableThread(function, data, processes=4)
            self.task.setDaemon(True)
            self.task.start()

            # self.pool = ThreadPool()
            # self.result = self.pool.map_async(function, data)
            # self.pool.close()
            #self.pool.join()
        #self.pool.close()
        #self.pool.join()
        #self.result = pickle_object(mapped)

        """Read an incoming message from the client and put it into our outgoing queue."""
        self.logger.debug('handle_read() -> (%d)', len(data))
        #self.result = all_data

    def handle_close(self):
        self.logger.debug('handle_close()')
        self.close()


    def handle_error(self):
        self.logger.debug('error occured!')


class Client(asyncore.dispatcher):
    """Sends messages to the server and receives responses.
    """

    def __init__(self, host, port, message, chunk_size=BUFFER_SIZE):
        asyncore.dispatcher.__init__(self)
        self.message_query = []
        self.message_query.append(message)
        self.chunk_size = chunk_size
        self.logger = logging.getLogger('Client')
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.logger.debug('connecting to %s', (host, port))
        self.connect((host, port))

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
        _ = self.sendall(to_send)

    def handle_read(self):
        input_data = []
        try:
            data = self.recv(self.chunk_size)
            while data:
                input_data.append(data)
                data = self.recv(self.chunk_size)
        except socket.error:
            #here got eof and an error. Don't know, why?
            pass
        all_data = ''.join(input_data)
        try:
            data = unpickle(all_data)
        except EOFError:
            #stackoverflow says that it is normal
            #self.logger.debug('Unexpected EOF!')
            pass

        if data == FAILED_MESSAGE:
            self.logger.debug(FAILED_MESSAGE)
        else:
            self.logger.debug('handle_read() "%s"',str(data))


    def send_message(self, message):
        self.message_query.append(message)

    def handle_error(self):
        self.logger.debug('Error ocured!')


def terminate_worker(client):
        time.sleep(5)
        client.send_message(TERMINATE_MESSAGE)


def test_function():
    address = ('localhost', 0) # let the kernel give us a port
    #address = (HOST, PORT)
    server = Server(address)
    ip, port = server.address # find out what port we were given

    from functions import foo
    pickled_data = pickle_object((foo,[(1,range(50000))] * 10**5))
    client = Client(ip, port, message=pickled_data)

    t = threading.Thread(target=terminate_worker, args=(client,))
    t.start()

    asyncore.loop(timeout=1)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='%(name)s: %(message)s',
                        )
    test_function()



