__author__ = 'happyin3 (happyinx3@gmail.com)'


def notfound_404(environ, start_response):
    start_response('404 Not Found', [('Content-type', 'text/plain')])
    return ['Not Found']


class Happy(object):

    def __init__(self):
        self.path_map = dict()

    def __call__(self, environ, start_response):
        method = environ['REQUEST_METHOD'].lower()
        path = environ['PATH_INFO']
        params = []
        if len(path.split('?')) == 2:
            params = path.split('?')[1].split('&')

        # params = cgi.FieldStorage(environ['wsgi.input'], environ=environ)
        # environ['params'] = {key: params.getvalue(key) for key in params}
        environ['params'] = {val.split('=')[0]: val.split('=')[1] for val in params}

        handler = self.path_map.get((method, path.split('?')[0]), notfound_404)
        return handler(environ, start_response)

    def register(self, method, path, function):
        self.path_map[method.lower(), path] = function
        return function
