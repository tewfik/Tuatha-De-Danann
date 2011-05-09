#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import socket
import threading

class ThreadSend(threading.Thread):
    """
    """

    def __init__(self, address, myId):
        threading.Thread.__init__(self)
        self.myId = myId
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect(address)
            self.sock.send('send ' + self.myId)
        except socket.error:
            print 'Send socket failed to connect to ' + str(address[0]) + ':' + str(address[1])
            sys.exit()


    def run(self):
        pass


class ThreadReceive(threading.Thread):
    """
    """

    def __init__(self, address, myId):
        threading.Thread.__init__(self)
        self.myId = myId
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect(address)
            self.sock.send('receive ' + self.myId)
        except socket.error:
            print 'Receive socket failed to connect to ' + str(address[0]) + ':' + str(address[1])
            sys.exit()


    def run(self):
        pass


def main(address):
    """
    Main program.

    Attributes:
    - `address`: (host, port)
        - `host`: address where Dana is hosted
        - `port`: port which Dana listen.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sock.connect(address)
    sock.send('register 0')
    myId = sock.recv(1024).strip()
    sock.close()

    th_S = ThreadSend(address, myId)
    th_R = ThreadReceive(address, myId)
    th_S.start()
    th_R.start()


if __name__ == '__main__':
    # command line argument management
    if(len(sys.argv) >= 3):
        host = sys.argv[1]
        port = int(sys.argv[2])
    else:
        host = 'localhost'
        port = 1337

    main((host,port))
