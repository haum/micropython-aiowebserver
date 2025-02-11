import aiowebserver as web

@web.route('GET', '/')
@web.route('GET', '/index.htm')
async def root_handler(rq):
    await rq.w('Hello, world!')

web.run_forever()
