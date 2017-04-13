import threading
import tincanchat
from tincanchat import HOST, PORT


def handle_client(sock, addr):
    try:
        msg = tincanchat.recv_msg(sock)
        print('{}: {}'.format(addr, msg))
        tincanchat.send_msg(sock, 'Echo from server: {}'.format(msg))
    except (ConnectionError, BrokenPipeError):
        print('Socket error')
    finally:
        print('Closed connection to {}'.format(addr))
        sock.close()

if __name__ == '__main__':
    listen_sock = tincanchat.create_listen_socket(HOST, PORT)
    addr = listen_sock.getsockname()
    print('Listening on {}'.format(addr))

    while True:
        client_sock, addr = listen_sock.accept()
        thread = threading.Thread(target=handle_client,
                                  args=[client_sock, addr],
                                  daemon=True)
        thread.start()
        print('Connection from {}'.format(addr))