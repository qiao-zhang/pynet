import asyncio
import tincanchat
from tincanchat import HOST, PORT

clients = []


class ChatServerProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        self.transport = transport
        self.addr = transport.get_extra_info('peername')
        self._rest = b''
        clients.append(self)
        print('Connection from {}'.format(self.addr))

    def data_received(self, data):
        data = self._rest + data
        msgs, self._rest = tincanchat.parse_recvd_data(data)
        for msg in msgs:
            msg = msg.decode('utf-8')
            msg = '{}: {}'.format(self.addr, msg)
            print(msg)
            msg = tincanchat.prep_msg(msg)
            for client in clients:
                client.transport.write(msg)

    def connection_lost(self, exc):
        print('Client {} disconnected'.format(self.addr))
        clients.remove(self)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    coroutine = loop.create_server(ChatServerProtocol,
                                   host=HOST, port=PORT)
    server = loop.run_until_complete(coroutine)

    for socket in server.sockets:
        addr = socket.getsockname()
        print('Listening on {}'.format(addr))
    loop.run_forever()
