# import pickle
#
#
# def foo(a,b):
#     return a + b
#
# string = pickle.dumps(foo)
# print string
#
# foo_ =  pickle.loads(string)
# print foo_
# print foo_(5,8)
from pickler import pickle_object, unpickle
import multiprocessing
from host_data import HOST, TERMINATE_MESSAGE,PORT

import asyncore
import logging


class Server(asyncore.dispatcher):
    """Receives connections and establishes handlers for each client.
    """

    def __init__(self, address):
        self.logger = logging.getLogger('Server')
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bind(address)
        self.address = self.socket.getsockname()
        self.logger.debug('binding to %s', self.address)
        self.listen(1)
        return

    def handle_accept(self):
        # Called when a client connects to our socket
        client_info = self.accept()
        self.logger.debug('handle_accept() -> %s', client_info[1])
        InfoHandler(sock=client_info[0])
        # We only want to deal with one client at a time,
        # so close as soon as we set up the handler.
        # Normally you would not do this and the server
        # would run forever or until it received instructions
        # to stop.
        self.handle_close()
        return

    def handle_close(self):
        self.logger.debug('handle_close()')
        self.close()
        return

class InfoHandler(asyncore.dispatcher):
    """Handles echoing messages from a single client.
    """

    def __init__(self, sock, chunk_size=25):
        self.chunk_size = chunk_size
        self.logger = logging.getLogger('InfoHandler%s' % str(sock.getsockname()))
        asyncore.dispatcher.__init__(self, sock=sock)
        self.result = None
        return

    def writable(self):
        """We want to write if we have received data."""
        response = bool(self.result)
        self.logger.debug('writable() -> %s', response)
        return response

    def handle_write(self):
        """Write as much as possible of the most recent message we have received."""
        data = self.result
        sent = self.sendall(data)
        self.result = False
        #self.logger.debug('handle_write() -> (%d) "%s"', sent, data[:sent])
        if not self.writable():
            self.handle_close()

    def handle_read(self):
        input_data = []
        data = self.recv(self.chunk_size)
        if data == TERMINATE_MESSAGE:
            return
        try:
            while data:
                input_data.append(data)
                data = self.recv(self.chunk_size)
        except socket.error:
            pass
        all_data = ''.join(input_data)
        function, data = unpickle(all_data)
        pool = multiprocessing.Pool()
        mapped = pool.map(function, data)
        pool.close()
        pool.join()
        self.result = pickle_object(mapped)

        """Read an incoming message from the client and put it into our outgoing queue."""
        self.logger.debug('handle_read() -> (%d) "%s"', len(data), data)
        #self.result = all_data

    def handle_close(self):
        self.logger.debug('handle_close()')
        self.close()


    def handle_error(self):
        print 'error occured!'



class Client(asyncore.dispatcher):
    """Sends messages to the server and receives responses.
    """

    def __init__(self, host, port, message, chunk_size=512):
        self.message = message
        self.to_send = message
        self.received_data = []
        self.chunk_size = chunk_size
        self.logger = logging.getLogger('EchoClient')
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.logger.debug('connecting to %s', (host, port))
        self.connect((host, port))
        return

    def handle_connect(self):
        self.logger.debug('handle_connect()')

    def handle_close(self):
        self.logger.debug('handle_close()')
        self.close()
        received_message = ''.join(self.received_data)
        data = unpickle(received_message)
        print data

    def writable(self):
        self.logger.debug('writable() -> %s', bool(self.to_send))
        return bool(self.to_send)

    def handle_write(self):
        sent = self.sendall(self.to_send)
        self.logger.debug('handle_write() ->"%s"',self.to_send[:sent])
        self.to_send = None

    def handle_read(self):
        data = self.recv(self.chunk_size)
        self.logger.debug('handle_read() -> (%d) "%s"', len(data), data)
        self.received_data.append(data)


def foo((k,v)):
    return (k,sum(v))

if __name__ == '__main__':
    import socket

    logging.basicConfig(level=logging.DEBUG,
                        format='%(name)s: %(message)s',
                        )

    address = ('localhost', 0) # let the kernel give us a port
    server = Server(address)
    ip, port = server.address # find out what port we were given

    pickled_data = pickle_object((foo,[(1,(1,2,3,4,5))]))
    client = Client(ip, port, message=pickled_data)

    asyncore.loop()