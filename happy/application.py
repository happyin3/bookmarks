'''web framework'''

__author__ = 'happyin3 (happyinx3@gmail.com)'


def application(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/html')])
    return [b'<h1>Hello, web!</h1>']
