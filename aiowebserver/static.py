import asyncio
import binascii
import deflate
import gc
import hashlib
import os
from .router import Http404

global_mimetypes = {
    'html': 'text/html',
    'htm': 'text/html',
    'css': 'text/css',
    'js': 'text/javascript',
    'json': 'application/json',
    'jpg': 'image/jpeg',
    'png': 'image/png',
    'py': 'text/x-python',
    'svg': 'image/svg+xml',
    'webp': 'image/webp',
    'ogg': 'audio/ogg',
    'mp3': 'audio/mp3',
    'wav': 'audio/wav',
    'ico': 'image/x-icon',
}

static_lock = asyncio.Lock()

async def sendfile(w, f, sz=4096):
    chunk = bytearray(sz)
    fr = f.readinto
    wr = w.write
    wd = w.drain
    while True:
        nb = fr(chunk)
        if nb == 0:
            break
        wr(memoryview(chunk)[0:nb])
        await wd()

def simplify_path(path):
    cs = path.split('/')
    s = []
    for c in cs:
        if c == '' or c == '.': continue
        elif c == '..': s.pop()
        else: s.append(c)
    return '/'.join(s)

def is_directory(path):
    try:
        s = os.stat(path)
        return (s[0] & 0x4000) != 0
    except OSError:
        return False

def is_file(path):
    try:
        s = os.stat(path)
        return (s[0] & 0x8000) != 0
    except OSError:
        return False

async def static_response(rq, path, directory='.', mimetypes=None):
    raw = True
    gz = False
    filepath = directory + '/' + simplify_path(path)
    if is_directory(filepath):
        if is_file(filepath + '/index.htm') or is_file(filepath + '/index.htm.gz'):
            filepath += '/index.htm'
    if not is_file(filepath):
        filepath += '.gz'
        gz = True
        if not 'gzip' in rq.headers.get('accept-encoding', '').split(', '):
            raw = False
    if not is_file(filepath):
        raise Http404()

    async with static_lock:
        etag = binascii.hexlify(
            hashlib.sha256(filepath + str(os.stat(filepath)[8])).digest()
        )
        if rq.headers.get('if-none-match', '""')[1:-1].encode() == etag:
            await rq.return_status(304)
            await rq.w(None, True)
            return
        ext = path.split('.')[-1]
        ctype = 'application/octet-stream'
        if type(mimetypes) is str:
            ctype = mimetypes
        elif mimetypes and ext in mimetypes:
            ctype = mimetypes[ext]
        elif ext in global_mimetypes:
            ctype = global_mimetypes[ext]
        elif mimetypes and '*' in mimetypes:
            ctype = mimetypes['*']
        if ctype.startswith('text/'):
            ctype += '; charset=utf-8'

        await rq.header('Content-Type', ctype)
        await rq.header('ETag', etag)
        await rq.header('Cache-Control', 'max-age=10, must-revalidate')
        await rq.header('Access-Control-Allow-Origin', '*')
        if gz: await rq.header('Content-Encoding', 'gzip')
        if raw: await rq.header('Content-Length', str(os.stat(filepath)[6]))
        await rq.w(None, True)

        gc.collect()
        if raw:
            with open(filepath, 'rb') as f:
                await sendfile(rq._w, f)
        else:
            with open(filepath, 'rb') as f:
                with deflate.DeflateIO(f, deflate.GZIP) as d:
                    await sendfile(rq._w, d)
