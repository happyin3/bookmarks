# -*- coding: utf-8 -*-

'''
IO多路复用服务器
'''

__author__ = 'happyin3 (happyinx3@gmail.com)'


import select
import math

from abc import ABCMeta, abstractmethod
from collections import namedtuple, Mapping


# generic events, that must be mapped to implementation-specific ones
EVENT_READ = (1 << 0)
EVENT_WRITE = (1 << 1)


def _fileobj_to_fd(fileobj):
    '''Return a file descriptor from a file object.'''
    if isinstance(fileobj, int):
        fd = fileobj
    else:
        try:
            fd = int(fileobj.fileno())
        except (AttributeError, TypeError, ValueError):
            raise ValueError('Invalid file object: '
                             '{!r}'.format(fileobj)) from None
    if fd < 0:
        raise ValueError('Invalid file descriptor: {}'.format(fd))
    return fd


SelectorKey = namedtuple('SelectorKey', ['fileobj', 'fd', 'events', 'data'])


class _SelectorMapping(Mapping):
    '''Mapping of file objects to selector keys.'''

    def __init__(self, selector):
        self._selector = selector

    def __len__(self):
        return len(self._selector._fd_to_key)

    def __getitem__(self, fileobj):
        try:
            fd = self._selector._fileobj_lookup(fileobj)
            return self._selector._fd_to_key[fd]
        except KeyError:
            raise KeyError('{!r} is not registered'.format(fileobj)) from None

    def __iter__(self):
        return iter(self._selector._fd_to_key)


class BaseSelector(metaclass=ABCMeta):
    '''Selector abstract base class.'''

    @abstractmethod
    def register(self, fileobj, events, data=None):
        raise NotImplementedError

    @abstractmethod
    def unregister(self, fileobj):
        raise NotImplementedError

    def modify(self, fileobj, events, data=None):
        self.unregister(fileobj)
        return self.register(fileobj, events, data)

    @abstractmethod
    def select(self, timeout=None):
        raise NotImplementedError

    def close(self):
        pass

    def get_key(self, fileobj):
        mapping = self.get_map()
        if mapping is None:
            raise RuntimeError('Selector is closed')
        try:
            return mapping[fileobj]
        except KeyError:
            raise KeyError('{!r} is not registered'.format(fileobj)) from None

    @abstractmethod
    def get_map(self):
        raise NotImplementedError

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


class _BaseSelectorImpl(BaseSelector):
    '''Base selector implementation.'''

    def __init__(self):
        # this maps file descriptors to keys
        self.__fd_to_key = {}
        # read-only mapping returned by get_map()
        self._map = _SelectorMapping(self)

    def _fileobj_lookup(self, fileobj):
        '''Return a file descriptor from a file object.'''
        try:
            return _fileobj_to_fd(fileobj)
        except ValueError:
            # Do an exhaustive search.
            for key in self._fd_to_key.values():
                if key.fileobj is fileobj:
                    return key.fd
            # Raise ValueError after all.
            raise

    def register(self, fileobj, events, data=None):
        if (not events) or (events & ~(EVENT_READ | EVENT_WRITE)):
            raise ValueError('Invalid events: {!r}'.format(events))

        key = SelectorKey(fileobj, self._fileobj_lookup(fileobj), events, data)

        if key.fd in self._fd_to_key:
            raise KeyError('{!r} (FD {}) is already registered'
                           .format(fileobj, key.fd))

        self._fd_to_key[key.fd] = key
        return key

    def unregister(self, fileobj):
        try:
            key = self._fd_to_key.pop(self._fileobj_lookup(fileobj))
        except KeyError:
            raise KeyError('{!r} is not registered'.format(fileobj)) from None
        return key

    def modify(self, fileobj, events, data=None):
        # TODO: Subclasses can probably optimize this even further.
        try:
            key = self._fd_to_key[self._fileobj_lookup(fileobj)]
        except KeyError:
            raise KeyError('{!r} is not registered'.format(fileobj)) from None

        if events != key.events:
            self.unregister(fileobj)
            key = self.register(fileobj, events, data)
        elif data != key.data:
            # Use a shortcut to update the data
            key = key._replace(data=data)
            self._fd_to_key[key.fd] = key
        return key

    def close(self):
        self._fd_to_key.clear()
        self._map = None

    def get_map(self):
        return self._map

    def _key_from_fd(self, fd):
        '''Return the key associated to a given file descriptor.'''
        try:
            return self._fd_to_key[fd]
        except KeyError:
            return None


class SelectorSelector(_BaseSelectorImpl):
    '''Select-based selector.'''

    def __init__(self):
        super().__init__()


if hasattr(select, 'epoll'):

    class EpollSelector(_BaseSelectorImpl):
        '''Epoll-based selector.'''

        def __init__(self):
            super().__init__()
            self._epoll = select.epoll()

        def fileno(self):
            return self._epoll.fileno()

        def register(self, fileobj, events, data=None):
            key = super().register(fileobj, events, data)
            epoll_events = 0
            if events & EVENT_READ:
                epoll_events |= select.EPOLLIN
            if events & EVENT_WRITE:
                epoll_events |= select.EPOLLOUT
            try:
                self._epoll.register(key.fd, epoll_events)
            except BaseException:
                super().unregister(fileobj)
                raise
            return key

        def unregister(self, fileobj):
            key = super().unregister(fileobj)
            try:
                self._epoll.unregister(key.fd)
            except OSError:
                # This can happen if the FD was closed since it
                # was registered.
                pass
            return key

        def select(self, timeout=None):
            if timeout is None:
                timeout = -1
            elif timeout <= 0:
                timeout = 0
            else:
                # epoll_wait() has a resolution of 1 millisecond, roundaway
                # from zero to wait *at least* timeout seconds.
                timeout = math.ceil(timeout * 1e3) * 1e-3

            # epoll_wait() expects `maxevents` to be greater than aero;
            # we want to make sure that `select()` can be called when no
            # FD is registered
            max_ev = max(len(self._fd_to_key), 1)

            ready = []
            try:
                fd_event_list = self._epoll.poll(timeout, max_ev)
            except InterruptedError:
                return ready
            for fd, event in fd_event_list:
                events = 0
                if event & ~select.EPOLLIN:
                    events |= EVENT_WRITE
                if event & ~select.EPOLLOUT:
                    events |= EVENT_READ

                key = self._key_from_fd(fd)
                if key:
                    ready.append((key, events & key.__events))
            return ready

        def close(self):
            self._epoll.close()
            super().close()


# Choose the best implementation, roughly:
#   epoll|kqueue|devpoll > poll > select.
# select() also can't accept a FD > FD_SETSIZE (usually around 1024)


'''
if 'KqueueSelector' in globals():
    DefaultSelector = KqueueSelector
elif 'EpollSelector' in globals():
    DefaultSelector = EpollSelector
elif 'DevpollSelector' in globals():
    DefaultSelector = DevpollSelector
elif 'PollSelector' in globals():
    DefaultSelector = PollSelector
else:
    DefaultSelector = SelectSelector
'''


DefaultSelector = EpollSelector
