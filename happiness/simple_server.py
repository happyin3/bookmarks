# -*- coding: utf-8 -*-


import socket
import functools

from simple_ioloop import IOLoop


ioloop = IOLoop()
EVENT_READ = ioloop.READ
EVENT_WRITE = ioloop.WRITE


def make_sock():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setblocking(0)
    sock.bind(('', 8889))
    sock.listen(128)
    return sock


def connection_ready(sock, fd, events):
    print('call connect ready')
    while True:
        try:
            connection, addr = sock.accept()
        except Exception:
            raise
        connection.setblocking(0)
        handler_connection(connection, addr)


def handler_connection(conn, addr):
    print('handler connection')
    callback = functools.partial(handler_read, conn)
    ioloop.register(conn.fileno(), callback, EVENT_READ)


def handler_read(conn, fd, event):
    print('handler read')
    msg = conn.recv(1024)
    print('get msg {}'.format(msg))
    callback = functools.partial(handler_write, conn)
    ioloop.modify(conn.fileno(), callback, EVENT_WRITE)


def handler_write(conn, fd, event):
    print('handler write')
    response = """HTTP/1.0 200 OK\r
        Date: Mon, 1 Jan 1996 01:01:01 GMT\r
        Content-Type: text/plain\r
        Content-Length: 13\r
        \r
        Hello, world!"""

    try:
        conn.send(bytes(response, encoding='utf8'))
        print('send')
    except Exception as e:
        print(e)
    finally:
        ioloop.unregister(conn.fileno())
        conn.close()


if __name__ == '__main__':
    sock = make_sock()
    callback = functools.partial(connection_ready, sock)
    ioloop.register(sock.fileno(), callback, EVENT_READ)
    ioloop.start()
