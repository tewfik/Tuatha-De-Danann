#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import network
import render
from area import Area

HEIGHT = 24
WIDTH = 32
TITLE = 'Tuatha dé Danann'
FPS = 40

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
    network.connection_start((host,port))

    display = render.Render(HEIGHT, WIDTH, 32, TITLE, FPS)
    display.load_map('../shared/etain.map')
    display.run()
