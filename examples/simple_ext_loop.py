import asyncio
import aiowebserver as web

@web.route('GET', '/')
@web.route('GET', '/index.htm')
async def root_handler(rq):
    await rq.w('Hello, world!')


async def counter():
    for i in range(1000):
        print('Counter:', i)
        await asyncio.sleep(1)


loop = asyncio.get_event_loop()

loop.create_task(counter())
loop.create_task(web.start())

try:
    loop.run_forever()
except KeyboardInterrupt:
    print('Stopping server')
    web.stop()
