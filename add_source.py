'''add link script'''

__author__ = 'happyin3 (happyinx3@gmail.com)'


import fire
import json
import datetime


def add(k, t, l, tag):
    kind, title, link, tag = k, t, l, tag
    data = dict(
        title=str(title),
        link=str(link),
        tags=[str(tag)],
        created=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    )
    print(data)

    file_path = 'ref.json'
    if kind == 'w':
        file_path = 'ref_website.json'

    links = dict(links=[])
    with open(file_path, 'r') as f:
        links = json.load(f)

    links['links'].append(data)

    with open(file_path, 'w') as f:
        json.dump(links, f)


if __name__ == '__main__':
    fire.Fire(add)
