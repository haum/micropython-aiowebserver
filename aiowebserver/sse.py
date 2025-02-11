class EventSource:

    @classmethod
    async def upgrade(cls, rq):
        await rq.header('Content-Type', 'text/event-stream')
        await rq.header('Cache-Control', 'no-cache')
        await rq.header('Connection', 'keep-alive')
        await rq.header('Access-Control-Allow-Origin', '*')
        await rq.w(None, True)
        return cls(rq._w)

    def __init__(self, w):
        self.w = w

    async def send(self, msg, id=None, event=None):
        w = self.w
        if id is not None:
            w.write(b'id: {}\r\n'.format(id))
        if event is not None:
            w.write(b'event: {}\r\n'.format(event))
        w.write(b'data: {}\r\n'.format(msg))
        w.write(b'\r\n')
        await w.drain()
