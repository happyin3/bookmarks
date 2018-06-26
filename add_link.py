'''add link script'''

__author__ = 'happyin3 (happyinx3@gmail.com)'


import fire
import json
import datetime


def add(title, link, tag):
    data = dict(
        title=str(title),
        link=str(link),
        tags=[str(tag)],
        created=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    )
    print(data)

    links = dict(links=[])
    with open('ref.json', 'r') as f:
        links = json.load(f)

    links['links'].append(data)

    with open('ref.json', 'w') as f:
        json.dump(links, f)


if __name__ == '__main__':
    fire.Fire(add)
