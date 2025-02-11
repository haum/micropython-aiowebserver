from .server import Server
from .router import Router, Http404

router = Router()
server = Server()

async def start(host='0.0.0.0', port=[80, 8000], server=server, router=router):
    await server.start(host, port, router)

def stop(server=server):
    server.stop()

def route(method, path, wildcard=False, router=router):
    def wrapper(handler):
        router.route(method, path, wildcard, handler)
        return handler
    return wrapper

def route_ws(path, router=router):
    def wrapper(handler):
        async def wsloop(rq):
            await rq.promote_websocket()
            await handler(rq, { 'type': 'open' })
            while True:
                evt = await rq.r()
                if evt is None: evt = { 'type': 'close' }
                await handler(rq, evt)
                if evt['type'] == 'close':
                    break
        router.route('GET', path, False, wsloop)
        return handler
    return wrapper

def route_sse(path, router=router):
    def wrapper(handler):
        async def sseinit(rq):
            await rq.promote_sse()
            await handler(rq)
        router.route('GET', path, False, sseinit)
        return handler
    return wrapper

def e404(router=router):
    def wrapper(handler):
        router.set_e404(handler)
        return handler
    return wrapper

from .run import run_forever
