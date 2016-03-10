import socket
from host_data import HOST, PORT
<<<<<<< HEAD
from pickler import pickle_object
=======
>>>>>>> master


def send_to(data, host=HOST, port=PORT):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
<<<<<<< HEAD
    client_socket.send(data)
    client_socket.close()
=======
    client_socket.sendto(data)
>>>>>>> master


def send_data(data):
    send_to(data)
    return True

<<<<<<< HEAD
if __name__ == '__main__':
    send_data(pickle_object(((500,800),(780,5),('ghg',))))
=======
>>>>>>> master
