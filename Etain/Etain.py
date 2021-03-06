#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import threading
import Queue
import network
import render
from area import Area
from locales import *

if __name__ == '__main__':
    # command line argument management
    if len(sys.argv) >= 4:
        nickname = sys.argv[1]
        host = sys.argv[2]
        port = int(sys.argv[3])
    elif len(sys.argv) == 3:
        host = 'localhost'
        nickname = sys.argv[1]
        port = int(sys.argv[2])
    elif len(sys.argv) == 2:
        host = 'localhost'
        port = 1337
        nickname = sys.argv[1]
    else:
        host = 'localhost'
        port = 1337
        nickname = raw_input('Veuillez indiquer votre nickname : ')

    # queues initialization: communication between network threads and game logic thread (which is in render)
    send_queue = Queue.Queue()
    receive_queue = Queue.Queue()

    # network connection
    network.connection_start((host,port), send_queue, receive_queue)
    print('network engine is running')

    # render's operations have to be in the main thread.
    display = render.Render(send_queue, receive_queue, '../shared/village.map', nickname)
    display.run()
