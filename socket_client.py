import socket
from host_data import HOST, PORT


def send_to(data, host=HOST, port=PORT):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    client_socket.sendto(data)


def send_data(data):
    send_to(data)
    return True

