import json
import aiowebserver as web

page_design_start = '''<!DOCTYPE html>
<html>
 <head>
   <title>aiowebserver example</title>
   <style>
     body {
       background-color: #333;
       display: flex;
       justify-content: center;
       align-items: center;
       height: 100vh;
       margin: 0;
       flex-direction: column;
       gap: 10px;
     }
     .box {
       background-color: white;
       color: #16a;
       padding: 20px;
       border-radius: 20px;
       text-align: center;
       min-width: 400px;
     }
     input {
        width: 100%;
     }
     a {
        color: #aa0;
        font-weight: bold;
        text-decoration: none;
     }
   </style>
 </head>
 <body>
'''
page_design_end = '''
 </body>
</html>'''


@web.e404()
async def e404_handler(rq):
    await rq.return_status(404)
    await rq.w(page_design_start)
    await rq.w('<div class="box">', False)
    await rq.w('<h1>Error 404</h1>', False)
    await rq.w('<p>File not found</p>', False)
    await rq.w('</div>', False)
    await rq.w('<div class="box">', False)
    await rq.w('<p>Path: <code>' + rq.path + '</code></p>')
    if rq.query:
        await rq.w('<p>Query: <code>' + str(rq.query) + '</code></p>')
    await rq.w('</div>', False)
    await rq.w(page_design_end)


@web.route('GET', '/')
@web.route('GET', '/index.htm')
async def root_handler(rq):
    await rq.w(page_design_start)

    await rq.w('<div class="box">', False)
    await rq.w('<h2>GET form</h2>', False)
    await rq.w('''<p>
    <form method="GET" action="/form_get">
        <input type="text" name="value" value="5" />
        <input type="range" name="array[]" value="42" />
        <input type="range" name="array[]" value="33" />
        <select name="option">
          <option value="opt1">Option 1</option>
          <option value="op2">Option 2</option>
          <option value="o3">Option 3</option>
        </select>
        <input type="checkbox" name="check" />
        <input type="submit" />
    </form>
</p>''', False)
    await rq.w('</div>', False)

    await rq.w('<div class="box">', False)
    await rq.w('<h2>POST form</h2>', False)
    await rq.w('''<p>
    <form method="POST" action="/form_post">
        <input type="text" name="value" value="5" />
        <input type="range" name="array[]" value="42" />
        <input type="range" name="array[]" value="33" />
        <select name="option">
          <option value="opt1">Option 1</option>
          <option value="op2">Option 2</option>
          <option value="o3">Option 3</option>
        </select>
        <input type="checkbox" name="check" />
        <input type="submit" />
    </form>
</p>''', False)
    await rq.w('</div>', False)

    await rq.w('<div class="box">', False)
    await rq.w('<h2>POST json</h2>', False)
    await rq.w('<p><button id="jsonbtn">Send json</button></p>', False)
    await rq.w('<p id="jsonres"></p>', False)
    await rq.w('''<script type="module">
    document.getElementById("jsonbtn").addEventListener('click', async () => {
        const data = {'option': 'opt1', 'value': '5', 'array[]': ['42', '33']};
        const response = await fetch('/form_json', {
            method: "post",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });
        const json = await response.json();
        document.getElementById("jsonres").innerText = JSON.stringify(json);
    });
</script>''', False)
    await rq.w('</div>', False)

    await rq.w(page_design_end)


@web.route('GET', '/form_get')
async def form_get_handler(rq):
    await rq.w(page_design_start)
    await rq.w('<a href="/">&laquo; Retour</a>', False)
    await rq.w('<div class="box">', False)
    await rq.w('<h1>Form GET</h1>', False)
    await rq.w('<p>Query: <code>' + str(rq.query) + '</code></p>')
    await rq.w('</div>', False)
    await rq.w('<div class="box">', False)
    await rq.w(str(await rq.decode_query_data()), False)
    await rq.w('</div>', False)
    await rq.w(page_design_end)


@web.route('POST', '/form_post')
@web.route('GET', '/form_post') # Handle GET method in same handler
async def form_get_handler(rq):
    if not rq.is_postform():
        await rq.redirect('/', False)
        return
    await rq.w(page_design_start)
    await rq.w('<a href="/">&laquo; Retour</a>', False)
    await rq.w('<div class="box">', False)
    await rq.w('<h1>Form POST</h1>', False)
    await rq.w('</div>', False)
    if rq.is_postform():
        await rq.w('<div class="box">', False)
        data = await rq.decode_postform_data()
        await rq.w(str(data), False)
        await rq.w('</div>', False)
    await rq.w(page_design_end)


@web.route('POST', '/form_json')
@web.route('GET', '/form_json') # Handle GET method in same handler
async def form_json_handler(rq):
    if not rq.is_postjson():
        await rq.redirect('/', False)
        return
    data = await rq.decode_postjson_data()
    await rq.header('Content-Type', 'application/json')
    await rq.w('{ "status": "OK", "data": ' + json.dumps(data) + ' }')


web.run_forever()
