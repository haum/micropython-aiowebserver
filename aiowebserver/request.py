import json
from .static import static_response

def unquote_plus(s):
    out = []
    i = 0
    n = len(s)
    while i < n:
        c = s[i]
        i += 1
        if c == '+':
            out.append(' ')
        elif c == '%':
            out.append(chr(int(s[i:i + 2], 16)))
            i += 2
        else:
            out.append(c)
    return ''.join(out)


def parse_qs(s):
    out = {}
    for x in s.split('&'):
        kv = x.split('=', 1)
        key = unquote_plus(kv[0])
        kv[0] = key
        if len(kv) == 1:
            val = True
            kv.append(val)
        else:
            val = unquote_plus(kv[1])
            kv[1] = val
        tmp = out.get(key, None)
        if tmp is None:
            out[key] = val
        else:
            if isinstance(tmp, list):
                tmp.append(val)
            else:
                out[key] = [tmp, val]
    return out


class Request:
    def __init__(self, r, w):
        self._r = r
        self._w = w
        self._header_step = 0
        self.method = None
        self.path = ''
        self.query = None
        self.headers = {}

    async def r(self, n):
        return await self._r.read(n)

    async def w(self, data, drain=True):
        await self._ensure_send_data()
        if data: self._w.write(data)
        if drain: await self._w.drain()

    async def header(self, k, v):
        if self._header_step == 0: await self.return_status(200)
        if self._header_step == 1:
            self._w.write(b'' + k + ': ' + v + '\r\n')
        else:
            raise RuntimeError('Headers already sent')

    async def header_html(self):
        return await self.header('Content-Type', 'text/html; charset=utf-8')

    async def header_text(self):
        return await self.header('Content-Type', 'text/plain')

    async def header_json(self):
        return await self.header('Content-Type', 'application/json')

    async def redirect(self, url, permanent=False):
        await self.return_status(301 if permanent else 302)
        await self.header('Location', url)

    async def sendfile(self, path, directory='.', mimetypes=None):
        await static_response(self, path, directory, mimetypes)

    async def return_status(self, n, txt=None):
        if self._header_step == 0:
            if not txt:
                if n == 200: txt = 'OK'
                elif n == 301: txt = 'Moved Permanently'
                elif n == 302: txt = 'Found'
                elif n == 304: txt = 'Not Modified'
                elif n == 400: txt = 'Bad Request'
                elif n == 403: txt = 'Forbidden'
                elif n == 404: txt = 'Not Found'
                elif n == 405: txt = 'Method Not Allowed'
                elif n == 418: txt = 'I\'m a teapot'
                elif n == 500: txt = 'Internal Server Error'
                else:
                    raise RuntimeError('Not implemented status, provide associated text')
            self._header_step = 1
            self._w.write('HTTP/1.1 ' + str(n) + ' ' + txt + '\r\n')
        else:
            raise RuntimeError('HTTP status already sent')

    def is_postform(self):
        return self.headers.get('content-type', None) == 'application/x-www-form-urlencoded'

    async def decode_postform_data(self, n=1024):
        if self.is_postform():
            return parse_qs((await self._r.read(n)).decode())
        else:
            return {}

    def is_postjson(self):
        return self.headers.get('content-type', None) == 'application/json'

    async def decode_postjson_data(self, n=1024):
        try:
            return json.loads((await self._r.read(n)).decode())
        except ValueError:
            return {}

    async def decode_query_data(self):
        return parse_qs(self.query)

    async def promote_websocket(self):
        from .websocket import WebSocket
        self.ws = await WebSocket.upgrade(self)
        self.r = self.ws.recv
        self.w = self.ws.send

    async def promote_sse(self):
        from .sse import EventSource
        self.sse = await EventSource.upgrade(self)
        self.r = None
        self.w = self.sse.send

    async def _ensure_send_data(self):
        if self._header_step < 2:
            if self._header_step == 0:
                await self.return_status(200)
                await self.header_html()
            self._header_step = 2
            self._w.write('\r\n')
            await self._w.drain()

    async def _parse_first_line(self):
        line = await self._r.readline()
        if not line: return

        p = line.decode().split()
        if len(p) < 3: return

        self.method = p[0]
        self.path = p[1]

        p = self.path.split('?', 1)
        if len(p) < 2:
            self.query = None
        else:
            self.path = p[0]
            self.query = p[1]

    async def _parse_headers(self):
        while True:
            line = await self._r.readline()
            if not line: break

            line = line.decode()
            if line == '\r\n': break

            key, value = line.split(':', 1)
            self.headers[key.lower()] = value.strip()
