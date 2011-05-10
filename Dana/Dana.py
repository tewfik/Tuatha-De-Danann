#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

import network

if __name__ == '__main__':
    # command line argument management
    if(len(sys.argv) >= 2):
        port = int(sys.argv[1])
    else:
        port = 1337

    network.connection_start(port=port)
