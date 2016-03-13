from pickle_test import Client

from host_data import HOST,PORT, TERMINATE_MESSAGE
from pickler import pickle_object
import asyncore

import socket
if __name__ == '__main__':
    address = (HOST,PORT)
    client = Client(HOST,PORT, message=TERMINATE_MESSAGE)
    asyncore.loop()