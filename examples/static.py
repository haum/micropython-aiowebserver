import os
import aiowebserver as web

staticpath = '.'

async def list_files(rq, path):
    await rq.w('''<html>
    <head>
    </head>
    <body>''', False)
    for f in os.listdir(path):
        s = os.stat(path + '/' + f)
        if (s[0] & 0x4000) != 0: f += '/' # For directories, add slash
        await rq.w('<a href="{}{}">{}</a><br />'.format(path[len(staticpath):], f, f))
    await rq.w('''</body>
</html>''')

@web.route('GET', '/', True)
async def root_handler(rq):
    p = rq.path[1:]
    pf = staticpath + '/' + p
    try:
        if os.stat(pf)[0] & 0x4000: # If directory
            await list_files(rq, pf)
        else:
            await rq.sendfile(p, staticpath, mimetypes={'*': 'text/plain'})
    except OSError:
        raise web.Http404()

web.run_forever()
