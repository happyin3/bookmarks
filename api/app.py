__author__ = 'happyin3 (happyinx3@gmail.com)'


import json


from happy.happy import Happy


def get_bookmarks(environ, start_response):
    start_response('200 OK', [('Content-Type', 'application/json')])
    return json.dumps([('title', 'url')])


def create_app():
    app = Happy()

    app.register('GET', '/api/bookmarks/', get_bookmarks)

    return app


app = create_app()
