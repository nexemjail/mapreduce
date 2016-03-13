from host_data import HOST, PORT, TERMINATE_MESSAGE
from pickler import unpickle, pickle_object
import socket
import asyncore
import multiprocessing
from multiprocessing.connection import Listener, Client
from threading import Thread
import time
import os, sys

def process_data(client_socket):
    pass

BUFFER = 8192


def reduce_func((k,v)):
    return (k,sum(v))

class Server(asyncore.dispatcher):

    def __init__(self, address):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bind(address)
        self.address = self.socket.getsockname()
        self.listen(5)
        self.handler = None

    def handle_accept(self):

        client_info = self.accept()
        if not self.handler:
            self.handler = InfoHandler(client_info[0])
        else:
            del self.handler
            self.handler = None

    def handle_close(self):
        self.close()
        print 'closed'


class InfoHandler(asyncore.dispatcher):

    def __init__(self, sock, chunk_size = 8192):
        self.chunk_size = chunk_size
        asyncore.dispatcher.__init__(self,sock)
        self.result = False

    def writable(self):
        response = bool(self.result)
        return response

    def handle_read(self):
        data_chunks = []
        while True:
            data_part = self.recv(self.chunk_size)
            if data_part:
                if data_part == TERMINATE_MESSAGE:
                    break
                data_chunks.append(data_part)
            else:
                packed_data = ''.join(data_chunks)
                function, data = unpickle(packed_data)
                pool = multiprocessing.Pool()
                self.result = pool.map(function, data)
                print self.result
                self.handle_write()
                break

    def handle_write(self):
        if self.result:
            print 'self', self.result
            self.send(self.result)
            self.result = False

    def handle_close(self):
        self.close()

    def handle_write_event(self):
        pass



if __name__ == '__main__':
    server = Server((HOST,PORT))
    asyncore.loop()


