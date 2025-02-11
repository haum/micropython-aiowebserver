async def default_404(rq):
    await rq.return_status(404)
    await rq.w('Not Found')


class Http404(Exception):
    pass


class Router:
    def __init__(self):
        self.paths = {}
        self.e404 = default_404

    def route(self, method, path, wildcard, handler):
        if not method in self.paths:
            self.paths[method] = []
        self.paths[method].append((path, wildcard, handler))

    def set_e404(self, handler):
        self.e404 = handler

    async def dispatch(self, rq):
        if rq.method in self.paths:
            for path, wildcard, handler in self.paths[rq.method]:
                if (wildcard and rq.path.startswith(path)) or rq.path == path:
                    try:
                        await handler(rq)
                        return
                    except Http404:
                        pass
        await self.e404(rq)
