import socket
from host_data import HOST, PORT
from pickler import pickle_object


def send_to(data, host=HOST, port=PORT):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    client_socket.send(data)
    client_socket.close()


def send_data(data):
    send_to(data)
    return True

if __name__ == '__main__':
    send_data(pickle_object(((500,800),(780,5),('ghg',))))