import asyncio
from .request import Request

class Server:
    def __init__(self):
        self.sock = None
        self.router = None

    async def _connected(self, r, w):
        try:
            rq = Request(r, w)
            await rq._parse_first_line()
            await rq._parse_headers()
            if rq.method:
                await self.router.dispatch(rq)
        except:
            await w.wait_closed()
            raise
        await w.wait_closed()

    async def start(self, host, port, router):
        self.router = router
        if type(port) is int: port = [port]
        for p in port:
            try:
                self.sock = await asyncio.start_server(self._connected, host, p)
                return True
            except OSError:
                pass
        return False

    def stop(self):
        self.sock.close()
