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
    if(len(sys.argv) >= 3):
        host = sys.argv[1]
        port = int(sys.argv[2])
    elif(len(sys.argv) == 2):
        host = 'localhost'
        port = int(sys.argv[1])
    else:
        host = 'localhost'
        port = 1337

    # queues initialization: communication between network threads and game logic thread (which is in render)
    send_queue = Queue.Queue()
    receive_queue = Queue.Queue()

    # network connection
    network.connection_start((host,port), send_queue, receive_queue)
    print('network engine is running')

    # render's operations have to be in the main thread.
    display = render.Render(send_queue, receive_queue, '../shared/etain.map')
    display.run()
