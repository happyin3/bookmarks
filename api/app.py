__author__ = 'happyin3 (happyinx3@gmail.com)'


import json


from happy.happy import Happy


def get_bookmarks(environ, start_response):
    start_response('200 OK', [('Content-Type', 'application/json')])
    res = {
        'links': [
            {'title': 'Python concurrent.future 使用教程及源码初剖', 'link': 'https://manjusaka.itscoder.com/2017/11/28/something-about-concurrent-future/', 'tags': ['Python']},
            {'title': 'Python线程同步机制: Locks, RLocks, Semaphores, Conditions, Events和Queues', 'link': 'http://yoyzhou.github.io/blog/2013/02/28/python-threads-synchronization-locks/', 'tags': ['Python']},
            {'title': '不看绝对后悔的Linux三剑客之grep实战精讲', 'link': 'http://blog.51cto.com/hujiangtao/1923675', 'tags': ['Linux']},
            {'title': '不看绝对后悔的Linux三剑客之sed实战精讲', 'link': 'http://blog.51cto.com/hujiangtao/1923718', 'tags': ['Linux']},
            {'title': '不看绝对后悔的Linux三剑客之awk实战精讲', 'link': 'http://blog.51cto.com/hujiangtao/1923930', 'tags': ['Linux']},
            {'title': '网络编程之理论篇', 'link': 'https://juejin.im/post/5a535f8b518825733060c7bd', 'tags': ['网络编程']},
        ]
    }
    return json.dumps(res)


def create_app():
    app = Happy()

    app.register('GET', '/api/bookmarks/', get_bookmarks)

    return app


app = create_app()
