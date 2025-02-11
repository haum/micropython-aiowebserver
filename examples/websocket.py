import aiowebserver as web

@web.route('GET', '/')
@web.route('GET', '/index.htm')
async def root_handler(rq):
    await rq.w(b'''<html>
    <head>
        <script type="module">
            const out = document.getElementById('out');
            const input = document.getElementById('msg');
            const ws = new WebSocket('ws://' + document.location.host + '/ws');
            ws.onmessage = evt => {
                const el = document.createElement('div');
                el.innerText = evt.data;
                out.insertBefore(el, out.firstChild);
            };
            document.forms[0].onsubmit = evt => {
                evt.preventDefault();
                ws.send(input.value);
                input.value = '';
            };
        </script>
    </head>
    <body>
        <form>
            <input type="text" id="msg" />
            <input type="submit" />
        </form>
        <div id="out"></div>
    </body>
</html>''')

ws_clients = set()

@web.route_ws('/ws')
async def ws_handler(rq, evt):
    global ws_clients
    t = evt['type']

    if t == 'open':
        ws_clients.add(rq)
        await rq.w('Connected ;-)')

    if t == 'text':
        for c in ws_clients:
            await c.w(evt['data'])

    elif t == 'close':
        ws_clients.discard(rq)

web.run_forever()
