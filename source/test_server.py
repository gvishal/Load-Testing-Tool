from gevent import pywsgi

def hello_world(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/html'),("Access-Control-Allow-Origin", "*")])
    yield '<b>Hello world!</b>\n'

server = pywsgi.WSGIServer(
    ('', 8000), hello_world)

server.serve_forever()
