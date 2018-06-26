'''web server'''

__author__ = 'happyin3 (happyinx3@gmail.com)'


import sys
from happiness.server import make_server

SERVER_ADDRESS = (HOST, PORT) = '', 8888


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit('Provide a WSGI application object as module:callable')

    app_path = sys.argv[1]
    module, application = app_path.split(':')
    module = __import__(module, fromlist=[module.split('.')[0]])
    application = getattr(module, application)
    print('application', application)
    httpd = make_server(SERVER_ADDRESS, application)
    print('WSGIServer: Serving HTTP on port {port} ...\n'.format(port=PORT))
    httpd.serve_forever()
