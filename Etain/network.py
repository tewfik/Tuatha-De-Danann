#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import threading

# unique client identifier allocated by Dana to identify the client.
_client_id = None
# event to report that the client_id has been initialized
_client_id_is_set = threading.Event()
# these queues are used in communication between game logic thread and networks threads
_send_queue = None
_receive_queue = None

class ThreadSend(threading.Thread):
    """
    Thread sending command in the queue to the server
    """

    def __init__(self, address):
        """
        Initialize the send socket.

        Attributes:
        - `address`: a tuple (host, port) giving the address of Dana.
        """
        threading.Thread.__init__(self)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        close_connection = False
        try:
            self.sock.connect(address)
            print('Etain send thread is connected to Dana')
            self.sock.send("send")
        except socket.error as e:
            print('Send socket failed to connect to ' + str(address[0]) + ':' + str(address[1]))
            print(e)
            close_connection = True
        except IOError as e:
            if e.errno == errno.EPIPE:
                # broken pipe
                print(e)
                close_connection = True
            else:
                # other error
                print(e)
                close_connection = True

        if close_connection:
            self.end_connection()

    def run(self):
        """
        Main send loop.
        """
        global _client_id
        global _client_id_is_set
        global _send_queue

        # waiting for a client_id
        print('Send thread is waiting for client_id')
        _client_id_is_set.wait()

        close_connection = False
        while(not close_connection):
            try:
                msg = str(_client_id) +':'+ _send_queue.get()
                self.sock.send(msg)
                print('msg "%s" sent' % msg)
            except socket.error as e:
                print(e)
                close_connection = True
            except IOError as e:
                if e.errno == errno.EPIPE:
                    # broken pipe
                    print(e)
                    close_connection = True
                else:
                    # other error
                    print(e)
                    close_connection = True

        self.end_connection()


    def end_connection(self):
        """
        Close both send and receive's threads.
        """
        # TODO(tewfik): close properly connection here
        print("end connection")


class ThreadReceive(threading.Thread):
    """
    Thread receiving command from server and storing them into a queue.

    Attributes:
    - `sock`: socket used to receive data from Dana.
    """

    def __init__(self, address):
        """
        Initialize the receive socket.

        Attributes:
        - `address`: a tuple (host, port) giving the address of Dana.
        """
        global _client_id
        global _client_id_is

        threading.Thread.__init__(self)

        # connection to Dana
        close_connection = False
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect(address)
            print('Etain receive thread is connected to Dana')

            # ask Dana for a client id
            self.sock.send("receive")

            print('Receive thread is waiting for client_id')
            data_length = int(self.sock.recv(4).strip())
            data = self.sock.recv(data_length).strip()
            if not data:
                close_connection = True

        except socket.error as e:
            print 'Receive socket failed to connect to ' + str(address[0]) + ':' + str(address[1])
            print(e)
            close_connection = True
        except IOError as e:
            if e.errno == errno.EPIPE:
                # broken pipe
                print(e)
                close_connection = True
            else:
                # other error
                print(e)
                close_connection = True

        if close_connection:
            self.end_connection()
        else:
            try:
                # client id registration
                _client_id = int(data)
                _client_id_is_set.set()  # report that client id is set (used by the send thread)
                print('client_id = %d' % _client_id)
            except ValueError as e:
                print(e)
                close_connection = True


    def run(self):
        """
        Main receive loop.
        """
        global _receive_queue

        # main receive loop
        close_connection = False
        while not close_connection:
            data = None
            try:
                print("Etain: receive thread is listenning")
                data_length = int(self.sock.recv(4).strip())
                data = self.sock.recv(data_length).strip()
            except socket.error as e:
                print(e)
                close_connection = True
            except IOError as e:
                if e.errno == errno.EPIPE:
                    # broken pipe
                    print(e)
                    close_connection = True
                else:
                    print(e)
                    close_connection = True

            if(not data):
                close_connection = True
            else:
                print("dana message: %s" % data)
                _receive_queue.put(data)

        self.end_connection()


    def end_connection(self):
        """
        Close both send and receive's threads.
        """
        # TODO(tewfik): close properly connection here
        print("end connection")


def connection_start(address, send_queue, receive_queue):
    """
    Main program.

    Attributes:
    - `address`: (host, port)
        - `host`: address where Dana is hosted
        - `port`: port which Dana listen.
    - `send_queue`: queue which contains messages to send to Dana.
    - `receive_queue`: queue which contains messages to receive from Dana.
    """
    global _send_queue
    global _receive_queue

    _send_queue = send_queue
    _receive_queue = receive_queue

    th_S = ThreadSend(address)
    th_S.daemon = True

    th_R = ThreadReceive(address)
    th_R.daemon = True

    th_S.start()
    th_R.start()
