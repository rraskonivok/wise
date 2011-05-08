#!/usr/bin/env python

import os
#import sys

#from gevent import wsgi
#from gevent import socket
from gevent import monkey

monkey.patch_all()

import settings
import django.core.handlers.wsgi
from socketio import SocketIOServer

from django.core.management import setup_environ
setup_environ(settings)

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
application = django.core.handlers.wsgi.WSGIHandler()

PORT = 8000

from wise.utils.serving import run_with_reloader

@run_with_reloader
def start_server():
    print('Listening on http://127.0.0.1:%s' % PORT)
    #wsgi.WSGIServer(('', PORT), application, spawn=None).serve_forever()
    server = SocketIOServer(('', PORT), application, resource="socket.io")
    server.serve_forever()

#def use_socket():
#    SOCK = 'gevent.sock'
#    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
#
#    try:
#        os.remove(SOCK)
#    except OSError:
#        pass
#
#    sock.bind(SOCK)
#    os.chmod(SOCK,0770)
#    sock.listen(256)

if __name__ == '__main__':
    start_server()
