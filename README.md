micropython-aiowebserver
========================

A simple HTTP server for micropython. It uses asyncio to manage concurrency.

Install library
---------------

### With `mpremote`

`mpremote mip install github:haum/micropython-aiowebserver`

### With `mip`

```python
import mip
mip.install('github:haum/micropython-aiowebserver')
```

Import library
--------------

`import aiowebserver as web`

Event loop
----------

If you do not use `asyncio` in your project, just use the `run_forever` helping
function:

```python
import aiowebserver as web

# Add route handlers
# ...

web.run_forever()
```

With your own asyncio loop, just add an `asyncio` task:

```python
loop = asyncio.get_event_loop()
loop.create_task(web.start())
```

Routes
------

Defining routes can be done using decorators, that can be chained:

```python
@web.route('GET', '/')
@web.route('GET', '/index.htm')
async def root_handler(rq):
    await rq.w('Hello, world!')
```

This defines routes `/` and `/index.htm` using `GET` requests to be served by
`root_handler`. This function should be a coroutine (`async`), receives the
request object as parameter. Here, it prints `Hello, world!`.

Request helpers
---------------

### Reading and writing

To read the data part of the request, use `rq.r(n)` with `n` the number of bytes
to read.

To write an answer, use `rq.w(str, drain)` where `str` is the string to send and
`drain` is an optional parameter set to `False` to not wait for the message to
be sent, for example to buffer messages cut in several small pieces.

### Static files

It is possible to send static files with
`rq.sendfile(path, directory, mimetypes, timestamp)`, with `path` the only
mandatory parameter.

`path` and `directory` give respectively the path and the directory in which to
search for this path. Without `directory` the current working directory is used.

`mimetypes` is a dictionary, with a mimetype (value) associated to extensions
(key). The special extension `*` serves as fallback mimetype. A default
dictionary is used in addition to this optional parameter. Using a string
instead of a directory forces the mimetype without reading the default
dictionary.

If present, `timestamp` is used to calculate an ETAG based on this value and the
path of the file. This ETAG is used by modern browsers to avoid downloading the
file if they already have it in cache. It can be any string-convertible value,
but the conversion should be different from the one used with old files
versions. As a consequence, using the date of the last update can be a good
idea, hence the name of the parameter.

The function can send gzipped files. The path should be without the `.gz`
extension. If the path is a directory, it will serve `index.htm` inside.

The funcion uses a lock to avoid sending multiple files in parallell that could
saturate the low RAM of the target.

### Returned status

If not specified, the returned status of the page is `200 OK`.

To change it, you have to call `rq.return_status(code, code_text)` before
calling header or write functions. `code` is the status code, `code_text` is the
associated text meaning that can be omoitted for a few common statuses.

### Redirect

Redirecting can be done with `rq.redirect(url, permanent)` where `url` is the
URL to redirect to and `permanent` is an optional parameter set to `True` to
use a `301 Moved Permanently` status redirection. This function use header
redirection and therefore should be called alone.

### Headers

Custom headers can be added with `rq.header(name, value)`. Those headers have to
be added before sending content and after the optional `return_status`

Special methods help to send `Content-Type` header: `rq.header_html()`,
`rq.header_text()`, `rq.header_json()`.

### Forms

Some methods help to deal with forms, in particular `rq.is_postform()`,
`rq.decode_postform_data()`, `rq.is_postjson()`, `rq.decode_postjson_data()` and
`rq.decode_query_data()`.

See `forms_and_404.py` for usage example.

Examples
--------

Note that code to connect to a network or start an access point is not is not
present in the examples. You should have setup network before starting them.

See `examples` folder for examples.

- `simple.py` Simple example with an index page
- `simple_port.py` Same example, but defining the listening port
- `simple_ext_loop.py` Same example, but without using `run_forever` helper
  function and with another counting task
- `forms_and_404.py` Example with different form handling (GET, POST, JSON) and
  a custom 404 error page
- `static.py` Example of static file serving
- `eventsourse.py` Example of SSE/EventSource event communication
- `websocket.py` Example of websocket communication

Initial tests
-------------

Initially tested with micropython 1.24 on unix and ESP32-C3 ports.
