from hashlib import sha1
from binascii import b2a_base64
import struct

class WebSocket:

    HANDSHAKE_KEY = b'258EAFA5-E914-47DA-95CA-C5AB0DC85B11'

    OP_TYPES = {
        0x0: 'cont',
        0x1: 'text',
        0x2: 'bytes',
        0x8: 'close',
        0x9: 'ping',
        0xa: 'pong',
    }

    @classmethod
    async def upgrade(cls, rq):
        key = rq.headers.get('sec-websocket-key', '').encode()
        key += WebSocket.HANDSHAKE_KEY
        x = b2a_base64(sha1(key).digest()).strip()
        await rq.return_status(101, 'Switching Protocols')
        await rq.header('Upgrade', 'websocket')
        await rq.header('Connection', 'Upgrade')
        await rq.header('Sec-WebSocket-Accept', x)
        await rq.w(None, True)
        return cls(rq._r, rq._w)

    def __init__(self, r, w):
        self.r = r
        self.w = w

    async def recv(self):
        r = self.r
        x = await r.read(2)
        if not x or len(x) < 2:
            return None
        out = {}
        op, n = struct.unpack('!BB', x)
        out['fin'] = bool(op & (1 << 7))
        op = op & 0x0f
        if op not in WebSocket.OP_TYPES:
            raise None
        out['type'] = WebSocket.OP_TYPES[op]
        masked = bool(n & (1 << 7))
        n = n & 0x7f
        if n == 126:
            n, = struct.unpack('!H', await r.read(2))
        elif n == 127:
            n, = struct.unpack('!Q', await r.read(8))
        if masked:
            mask = await r.read(4)
        data = await r.read(n)
        if masked:
            data = bytearray(data)
            for i in range(len(data)):
                data[i] ^= mask[i % 4]
            data = bytes(data)
        if out['type'] == 'text':
            data = data.decode()
        out['data'] = data
        return out

    async def send(self, msg):
        if isinstance(msg, str):
            await self._send_op(0x1, msg.encode())
        elif isinstance(msg, bytes):
            await self._send_op(0x2, msg)

    async def _send_op(self, opcode, payload):
        w = self.w
        w.write(bytes([0x80 | opcode]))
        n = len(payload)
        if n < 126:
            w.write(bytes([n]))
        elif n < 65536:
            w.write(struct.pack('!BH', 126, n))
        else:
            w.write(struct.pack('!BQ', 127, n))
        w.write(payload)
        await w.drain()
