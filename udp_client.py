from socket import socket, AF_INET, SOCK_DGRAM

MAXSIZ = 4096
PORT = 12346

if __name__ == '__main__':
    sock = socket(AF_INET, SOCK_DGRAM)
    msg = "Hello UDP server"
    sock.sendto(msg.encode(), ('', PORT))
    data, addr = sock.recvfrom(MAXSIZ)
    print("Server says: ", repr(data))
