import asyncio
from . import start, stop

def run_forever(*args, **kwargs):
    loop = asyncio.get_event_loop()
    loop.create_task(start(*args, **kwargs))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print('Stopping server')
        stop()
