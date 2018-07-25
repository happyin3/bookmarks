# -*- coding: utf-8 -*-

import select


class IOLoop(object):

    ERROR = select.EPOLLERR | select.EPOLLHUP
    READ = select.EPOLLIN
    WRITE = select.EPOLLOUT

    def __init__(self):
        self.impl = select.epoll()
        self._events = {}
        self._handlers = {}

    def split_fd(self, fd):
        try:
            return fd.fileno(), fd
        except AttributeError:
            return fd, fd

    def register(self, fd, handler, events):
        fd, obj = self.split_fd(fd)
        self._handlers[fd] = (obj, handler)
        self.impl.register(fd, events | self.ERROR)

    def modify(self, fd, handler, events):
        fd, obj = self.split_fd(fd)
        self._handlers[fd] = (obj, handler)
        self.impl.modify(fd, events | self.ERROR)

    def unregister(self, fd):
        fd, obj = self.split_fd(fd)
        self._handlers.pop(fd, None)
        self._events.pop(fd, None)
        try:
            self.impl.unregister(fd)
        except Exception as e:
            print(e)

    def start(self):
        while True:
            try:
                event_pairs = self.impl.poll(2)
            except Exception as e:
                continue

            self._events.update(event_pairs)
            while self._events:
                fd, events = self._events.popitem()
                try:
                    fd_obj, handler_func = self._handlers[fd]
                    handler_func(fd_obj, events)
                except Exception as e:
                    print(e)
