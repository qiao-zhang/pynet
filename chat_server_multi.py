import threading
import queue
import tincanchat
from tincanchat import HOST, PORT

send_queues = {}
lock = threading.Lock()


def handle_client_recv(sock, addr):
    rest = bytes()
    while True:
        try:
            msgs, rest = tincanchat.recv_msgs(sock, rest)
        except (EOFError, ConnectionError):
            handle_disconnect(sock, addr)
            break
        for msg in msgs:
            msg = '{}: {}'.format(addr, msg)
            print(msg)
            broadcast_msg(msg)


def handle_client_send(sock, q, addr):
    while True:
        msg = q.get()
        if msg is None:
            break
        try:
            tincanchat.send_msg(sock, msg)
        except (ConnectionError, BrokenPipeError):
            handle_disconnect(sock, addr)
            break


def broadcast_msg(msg):
    with lock:
        for q in send_queues.values():
            q.put(msg)


def handle_disconnect(sock, addr):
    fd = sock.fileno()
    with lock:
        q = send_queues.get(fd, None)
        if q:
            q.put(None)
            del send_queues[fd]
            addr = sock.getpeername()
            print('Client {} disconnected'.format(addr))
            sock.close()


if __name__ == '__main__':
    listen_sock = tincanchat.create_listen_socket(HOST, PORT)
    addr = listen_sock.getsockname()
    print('Listening on {}'.format(addr))

    while True:
        client_sock, addr = listen_sock.accept()
        q = queue.Queue()
        with lock:
            send_queues[client_sock.fileno()] = q
        recv_thread = threading.Thread(target=handle_client_recv,
                                       args=[client_sock, addr],
                                       daemon=True)
        send_thread = threading.Thread(target=handle_client_send,
                                       args=[client_sock, q, addr],
                                       daemon=True)
        recv_thread.start()
        send_thread.start()
        print('Connection from {}'.format(addr))
