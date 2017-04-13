import tincanchat
from tincanchat import HOST, PORT


def handle_client(sock, addr):
    try:
        msg = tincanchat.recv_msg(sock)
        print('{}: {}'.format(addr, msg))
        tincanchat.send_msg(sock, msg)
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
        conn_sock, addr = listen_sock.accept()
        print('Connection from {}'.format(addr))
        handle_client(conn_sock, addr)
