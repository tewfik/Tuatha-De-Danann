#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import threading

class ThreadSend(threading.Thread):
    """
    Thread sending command in the queue to the server
    """

    def __init__(self, address, my_id):
        """
        Initialize the send socket.

        Attributes:
        - `address`: a tuple (host, port) giving the address of Dana.
        - `my_id`: unique id given by the server to identify the client.
        """
        threading.Thread.__init__(self)
        self.my_id = my_id
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        close_connection = False
        try:
            self.sock.connect(address)
            self.sock.send('send ' + self.my_id)
        except socket.error as e:
            print 'Send socket failed to connect to ' + str(address[0]) + ':' + str(address[1])
            print e
            close_connection = True
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
        """
        Main emission loop.
        """
        while(True):
            import time # DEBUG
            time.sleep(1) # DEBUG

            close_connection = False
            try:
                self.sock.send('coucou')
            except socket.error as e:
                print e
                close_connection = True
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
        """
        Close both send and receive's threads.
        """
        # TODO(tewfik): close properly connection here
        print "end connection"


class ThreadReceive(threading.Thread):
    """
    Thread receiving command from server and storing them into a queue.
    """

    def __init__(self, address, my_id):
        """
        Initialize the receive socket.

        Attributes:
        - `address`: a tuple (host, port) giving the address of Dana.
        - `my_id`: unique id given by the server to identify the client.
        """
        threading.Thread.__init__(self)
        self.my_id = my_id
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect(address)
            self.sock.send('receive ' + self.my_id)
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
        """
        Main receive loop.
        """
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

            if(close_connection or not data):
                self.end_connection()
                break

            print data


    def end_connection(self):
        """
        Close both send and receive's threads.
        """
        # TODO(tewfik): close properly connection here
        print "end connection"


def connection_start(address):
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
    my_id = sock.recv(1024).strip()
    sock.close()

    th_S = ThreadSend(address, my_id)
    th_S.daemon = True

    th_R = ThreadReceive(address, my_id)
    th_R.daemon = True

    th_S.start()
    th_R.start()
