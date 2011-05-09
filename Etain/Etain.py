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
        close_connection = False
        try:
            self.sock.connect(address)
            self.sock.send('send ' + self.myId)
        except socket.error as e:
            print 'Send socket failed to connect to ' + str(address[0]) + ':' + str(address[1])
            print e
            close_conneciton = True
        except IOError as e:
            if e.errno == errno.EPIPE:
                # broken pipe
                print e
                close_connection = True
            else:
                # other error
                print e
                close_connection = True

        if close_connection:
            self.end_connection()


    def run(self):
        while(True):
            import time # DEBUG
            time.sleep(1) # DEBUG

            close_connection = False
            try:
                self.sock.send('coucou')
            except socket.error as e:
                print 'Send socket failed to connect to ' + str(address[0]) + ':' + str(address[1])
                print e
                self.end_connection()
            except IOError as e:
                if e.errno == errno.EPIPE:
                    # broken pipe
                    print e
                    close_connection = True
                else:
                    # other error
                    print e
                    close_connection = True

            if close_connection:
                self.end_connection()
                break

    def end_connection(self):
        # TODO(tewfik): close properly connection here
        print "end connection"


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
        except socket.error as e:
            print 'Receive socket failed to connect to ' + str(address[0]) + ':' + str(address[1])
            print e
            self.end_connection()
        except IOError as e:
            if e.errno == errno.EPIPE:
                # broken pipe
                print e
                self.end_connection()
            else:
                # other error
                print e
                self.end_connection()


    def run(self):
        close_connection = False

        while(True):
            try:
                data = self.sock.recv(1024).strip()
            except socket.error as e:
                print e
                close_connection = True
            except IOError as e:
                if e.errno == errno.EPIPE:
                    # broken pipe
                    print e
                    close_connection = True
                else:
                    print e
                    close_connection = True

            if(close_connection):
                self.end_connection()
                break

            print data


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
    th_S.daemon = True

    th_R = ThreadReceive(address, myId)
    th_R.daemon = True

    th_S.start()
    th_R.start()

    th_S.join()
    th_R.join()


if __name__ == '__main__':
    # command line argument management
    if(len(sys.argv) >= 3):
        host = sys.argv[1]
        port = int(sys.argv[2])
    elif:
        host = 'localhost'
        port = int(sys.argv[1])
    else:
        host = 'localhost'
        port = 1337
    import signal
    main((host,port))
