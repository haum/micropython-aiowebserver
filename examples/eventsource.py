import asyncio
import aiowebserver as web

@web.route('GET', '/')
@web.route('GET', '/index.htm')
async def root_handler(rq):
    await rq.w(b'''<html>
    <head>
        <script type="module">
            const sse = new EventSource('/events');
            sse.onmessage = evt => {
                const el = document.createElement('p');
                el.innerText = evt.data;
                document.body.appendChild(el);
            };
        </script>
    </head>
    <body>
        <p>Events:</p>
    </body>
</html>''')

@web.route_sse('/events')
async def sse_handler(rq):
    for count in range(60):
        try:
            await rq.w('Event #{}'.format(count))
        except:
            break
        await asyncio.sleep(1)

web.run_forever()
