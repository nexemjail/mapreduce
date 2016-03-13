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
from host_data import HOST, TERMINATE_MESSAGE,PORT,FAILED_MESSAGE
from multiprocessing.pool import ThreadPool
import asyncore
import logging
import stoppable_thread
import socket
import threading

BUFFER_SIZE = 8192

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
        self.listen(5)
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

    def __init__(self, sock, chunk_size=BUFFER_SIZE):
        self.chunk_size = chunk_size
        self.logger = logging.getLogger('InfoHandler%s' % str(sock.getsockname()))
        asyncore.dispatcher.__init__(self, sock=sock)
        self.result = None
        self.pool  = None
        self.task = None
        return

    def writable(self):
        """We want to write if we have received data."""
        if isinstance(self.result, str):
            response = bool(self.result)
        else:
            response = bool(self.task and self.task.ready())
            self.logger.debug('writable() -> %s', bool(self.task and self.task.ready()))
        return response

    def handle_write(self):
        """Write as much as possible of the most recent message we have received."""
        if self.result == FAILED_MESSAGE:
            data = pickle_object(self.result)
        else:
            data = pickle_object(self.task.get())
        sent = self.sendall(data)
        self.result = None
        self.task = None
        #self.logger.debug('handle_write() -> (%d) "%s"', sent, data[:sent])
        if not self.writable():
            self.handle_close()

    def handle_read(self):
        input_data = []
        data = self.recv(self.chunk_size)
        if data == TERMINATE_MESSAGE:
            if self.task and not self.task.ready():
                self.task.terminate()
                print 'task terminated!'
                self.result = FAILED_MESSAGE
        else:
            try:
                while data:
                    input_data.append(data)
                    data = self.recv(self.chunk_size)
            except socket.error:
                pass
            all_data = ''.join(input_data)
            function, data = unpickle(all_data)
            self.task = stoppable_thread.StoppableThread(function, data,processes=4)
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


    #def handle_error(self):
    #    print 'error occured!'



class Client(asyncore.dispatcher):
    """Sends messages to the server and receives responses.
    """

    def __init__(self, host, port, message, chunk_size=BUFFER_SIZE):
        self.message_query = []
        #self.message = message
        #self.to_send = message
        self.message_query.append(message)
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
        # received_message = ''.join(self.received_data)
        # data = unpickle(received_message)
        # print data

    def writable(self):
        self.logger.debug('writable() -> %s', bool(self.message_query))
        return bool(self.message_query)

    def handle_write(self):
        to_send, self.message_query = self.message_query[0], self.message_query[1:]
        _ = self.sendall(to_send)
        #self.logger.debug('handle_write() ->"%s"',to_send)

    def handle_read(self):
        input_data = []
        try:
            data = self.recv(self.chunk_size)
            while data:
                input_data.append(data)
                data = self.recv(self.chunk_size)
        except socket.error:
            pass
        all_data = ''.join(input_data)
        data = unpickle(all_data)
        if data == FAILED_MESSAGE:
            print 'TERMINATED OR FAILED!'
        else:
            self.logger.debug('handle_read() "%s"',str(data[0]))

    def send_message(self, message):
        self.message_query.append(message)

def terminating(client,ip,port):
        time.sleep(6)
        client.send_message(TERMINATE_MESSAGE)#client.send_message(TERMINATE_MESSAGE)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='%(name)s: %(message)s',
                        )

    address = ('localhost', 0) # let the kernel give us a port
    #address = (HOST, PORT)
    server = Server(address)
    ip, port = server.address # find out what port we were given

    # def foo((k,v)):
    #     return (k,sum(v))

    from functions import foo
    import time
    pickled_data = pickle_object((foo,[(1,range(50000))] * 10**5))
    client = Client(ip, port, message=pickled_data)


    t = threading.Thread(target=terminating, args=(client, ip, port))
    t.start()

    asyncore.loop(use_poll=True,timeout=0.1)
    #client = Client(ip, port, message=TERMINATE_MESSAGE)
    #client.send_message(TERMINATE_MESSAGE)

