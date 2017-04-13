import select
import tincanchat
from types import SimpleNamespace
from collections import deque
from tincanchat import HOST, PORT

BUFSIZ = 4096
clients = {}


def create_client(sock):
    return SimpleNamespace(sock=sock, rest=bytes(), send_queue=deque())


def broadcast_msg(msg):
    """ Add message to all connected clients' queues"""
    data = tincanchat.prep_msg(msg)
    for client in clients.values():
        client.send_queue.append(data)
        poll.register(client.sock, select.POLLOUT)

if __name__ == '__main__':
    listen_socket = tincanchat.create_listen_socket(HOST, PORT)
    poll = select.poll()
    poll.register(listen_socket, select.POLLIN)
    addr = listen_socket.getsockname()
    print('Listening on {}'.format(addr))

    while True:
        for fd, event in poll.poll():
            # clear up the socket if it is closed
            if event & (select.POLLHUP | select.POLLERR | select.POLLNVAL):
                poll.unregister(fd)
                del clients[fd]
            # accept new connection
            elif fd == listen_socket.fileno():
                conn_sock, addr = listen_socket.accept()
                conn_sock.setblocking(False)
                fd = conn_sock.fileno()
                clients[fd] = create_client(conn_sock)
                poll.register(fd, select.POLLIN)
                print('Connection from {}'.format(addr))
            # handle received data
            elif event & select.POLLIN:
                client = clients[fd]
                addr = client.sock.getpeername()
                recvd = client.sock.recv(BUFSIZ)
                if not recvd:
                    client.sock.close()
                    print('Client {} disconnected'.format(addr))
                    continue
                data = client.rest + recvd
                msgs, client.rest = tincanchat.parse_recvd_data(data)
                for msg in msgs:
                    msg = '{}: {}'.format(addr, msg)
                    print(msg)
                    broadcast_msg(msg)
            # send message to ready client
            elif event & select.POLLOUT:
                client = clients[fd]
                data = client.send_queue.popleft()
                sent = client.sock.send(data)
                if sent < len(data):
                    client.sends.appendleft(data[sent:])
                if not client.send_queue:
                    poll.modify(client.sock, select.POLLIN)
