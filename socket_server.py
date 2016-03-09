import socket
import SocketServer

HOST = 'localhost'
PORT = 9952
SUCCSESS_MESSAGE = 'succ!'


def serve_responses():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    while True:
        client_socket, address = server_socket.accept()
        client_socket.send(SUCCSESS_MESSAGE)

if __name__ == '__main__':
    serve_responses()