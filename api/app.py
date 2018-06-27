__author__ = 'happyin3 (happyinx3@gmail.com)'


import json


from happy.happy import Happy


def get_links_by_tag(environ, start_response):
    start_response('200 OK', [('Content-Type', 'application/json')])

    tag = environ.get('params', {}).get('tag', '')

    res = json.dumps(dict(links=[]))
    with open('ref.json', 'r') as f:
        res = json.load(f)

    link_list = [link for link in res.get('links') if tag in link.get('tags', [])]

    res = json.dumps(dict(links=link_list))

    return res


def get_links(environ, start_response):
    start_response('200 OK', [('Content-Type', 'application/json')])

    res = json.dumps(dict(links=[]))
    with open('ref.json', 'r') as f:
        res = f.read()

    return res


def create_app():
    app = Happy()

    app.register('GET', '/api/links/', get_links)
    app.register('GET', '/api/tag/links/', get_links_by_tag)

    return app


app = create_app()
