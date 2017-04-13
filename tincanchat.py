import socket

HOST = ''
PORT = 4040
BUFSIZ = 4096


def create_listen_socket(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((host, port))
    sock.listen(100)
    return sock


def recv_msg(sock):
    data = bytearray()
    msg = ''
    while not msg:
        recvd = sock.recv(BUFSIZ)
        if not recvd:
            raise ConnectionError()
        data += recvd
        if b'\0' in recvd:
            msg = data.rstrip(b'\0')
    msg = msg.decode('utf-8')
    return msg


def prep_msg(msg):
    msg += '\0'
    return msg.encode('utf-8')


def send_msg(sock, msg):
    data = prep_msg(msg)
    sock.sendall(data)