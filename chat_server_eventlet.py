import eventlet
import eventlet.queue as queue
import tincanchat
from tincanchat import HOST, PORT

send_queues = {}


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
    """ Monitor queue for new message, send them to client as they arrive"""
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
    for q in send_queues.values():
        q.put(msg)


def handle_disconnect(sock, addr):
    fd = sock.fileno()
    q = send_queues.get(fd, None)
    if q:
        q.put(None)
        del send_queues[fd]
        # addr = sock.getpeername()
        print('Client {} disconnected'.format(addr))
        sock.close()


if __name__ == '__main__':
    server = eventlet.listen((HOST, PORT))
    addr = server.getsockname()
    print('Listening on {}'.format(addr))

    while True:
        conn_sock, addr = server.accept()
        q = queue.Queue()
        send_queues[conn_sock.fileno()] = q
        eventlet.spawn_n(handle_client_recv, conn_sock, addr)
        eventlet.spawn_n(handle_client_send, conn_sock, q, addr)
        print('Connection from {}'.format(addr))
