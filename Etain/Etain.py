#!/usr/bin/env python
# -*- coding: UTF8 -*-

import sys
import socket


def main((host,port)):
    """
    Main program.

    Attributes:
    - `host`: address where Dana is hosted
    - `port`: port which Dana listen.
    """


if __name__ == '__main__':
    # command line argument management
    if(len(sys.argv) >= 3):
        host = sys.argv[1]
        port = int(sys.argv[2])
    else:
        host = 'localhost'
        port = 1337

    main((host,port))
