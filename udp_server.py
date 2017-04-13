from socket import socket, AF_INET, SOCK_DGRAM

MAXSIZ = 4096

if __name__ == '__main__':
    sock = socket(AF_INET, SOCK_DGRAM)
    sock.bind(('', 12346))
    while True:
        data, addr = sock.recvfrom(MAXSIZ)
        print('Client {host}:{port} says: {msg}'.format(host=addr[0], port=addr[1], msg=data.decode('utf-8')))
        resp = "UDP server sending data"
        sock.sendto(resp.encode(), addr)
