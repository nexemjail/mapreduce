import socket
<<<<<<< Updated upstream
import SocketServer

HOST = 'localhost'
PORT = 9952
SUCCSESS_MESSAGE = 'succ!'

=======
from pickler import unpickle
BUFFER_SIZE = 1024
>>>>>>> Stashed changes

def serve_responses():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    while True:
        client_socket, address = server_socket.accept()
<<<<<<< Updated upstream
        client_socket.send(SUCCSESS_MESSAGE)

if __name__ == '__main__':
    serve_responses()
=======
        input_data = []
        while True:
            data = client_socket.recv(BUFFER_SIZE)
            if not data:
                full_data = ''.join(input_data)
                print unpickle(full_data)
                del input_data
                del data
                break
            input_data.append(data)


def run_server():
    _serve()


if __name__ == '__main__':
    run_server()
>>>>>>> Stashed changes
