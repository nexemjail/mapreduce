from host_data import HOST, PORT, TERMINATE_MESSAGE
import socket
from pickler import unpickle
from worker_process import WorkerProcess

BUFFER_SIZE = 1024


def _serve(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    while True:
        client_socket, address = server_socket.accept()
        input_data = []
        while True:
            data = client_socket.recv(BUFFER_SIZE)
            if not data:
                full_data = ''.join(input_data)

                if full_data == TERMINATE_MESSAGE:
                    if worker is not None and worker.is_alive():
                        worker.terminate()
                    return

                input_data = unpickle(full_data)
                function, data = input_data
                worker = WorkerProcess(data, function)
                worker.start()
                print 'done!'
                del input_data
                del data
                break
            input_data.append(data)


def run_server(host, port):
    _serve(host,port)


if __name__ == '__main__':
    run_server(HOST, PORT)
