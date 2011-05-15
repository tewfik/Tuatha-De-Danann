#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import threading
import Queue
import SocketServer

# last client identifier which was allocated.
last_id = 0

#
_dana_queue = None

class ThreadingTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer): pass


class TCPHandler(SocketServer.BaseRequestHandler):
    """
    """

    def register(self):
        """
        A client ask for an unique identifier.
        The server has to register the client id, his login and his (hashed) pass.
        """
        #get login/pass
        #client_id = AccountManagement.get_next_client_id()
        global _dana_queue
        global last_id

        # TODO(tewfik): asking to dana to generate the client id
        last_id += 1
        #
        try:
            self.request.send(str(last_id))
        except socket.error:
            print e
        except IOError as e:
            if e.errno == errno.EPIPE:
                # broken pipe
                print e
            else:
                # other error
                print e


    def send_loop(self, client_id):
        """
        Dana send data to the client.
        """
        global _dana_queue

        # create a queue which will be used by Dana to send data to the client
        client_queue = Queue.Queue()
        # ask for a client_id (client_id == 0 : request for a client_id) and send the queue's reference to Dana
        _dana_queue.put((0, client_queue))

        # main loop
        close_connection = False
        while not close_connection:
            # note that the first dana_request that Dana sends to the client is the client_id
            # TODO(tewfik): SECURITY: memoize the client_id (use in an ASSERT test?) and transmit it to the receive loop (SECURITY identification)

            # wait for a Queue event
            dana_request = client_queue.get()

            # send a client request
            try:
                self.request.send(dana_request)
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

            import time # DEBUG
            time.sleep(1) # DEBUG


    def receive_loop(self, client_id):
        """
        Dana receives data from the client, parses it and reacts to it.
        """
        global _dana_queue

        # main loop
        while True:
            try:
                # wait for request
                data = self.request.recv(1024).strip()
            except socket.error as e:
                print e
                data = ""
            except IOError as e:
                if e.errno == errno.EPIPE:
                    # broken pipe
                    data = ""
                    print e
                else:
                    # other error
                    data = ""
                    print e

            if(not data):
                self.end_connection()
                break

            # send the request to Dana
            _dana_queue.put(data)
            print "%s wrote: %s" % (self.client_address[0], data)


    def handle(self):
        """
        Handle requests and allocate them to the concerned handle function.
        => send_loop function : server send data to client
        => receive_loop funciton : server receive data from the client and reacts.
        """
        #TODO(tewfik): gérer la connexion des clients (login/pass)

        # choose between send connection and receive connection
        try:
            data = self.request.recv(1024).strip()
        except socket.error as e:
            print e
            raise
        except IOError as e:
            if e.errno == errno.EPIPE:
                # broken pipe
                print e
                raise
            else:
                # other error
                print e
                raise

        connection_type, client_id = data.split(" ")

        if connection_type  == "receive":
            self.send_loop(client_id)
        elif connection_type == "send":
            self.receive_loop(client_id)
        else:
            self.request.send("vtff")


    def end_connection(self):
        """
        """
        print "end connection"



def connection_start(queue, port, host='localhost'):
    """
    Launch the network listening.
    This is a blocking call.

    Attributes:
    - `host`: host
    - `port`: port which Dana listen.
    """
    global _dana_queue
    _dana_queue  = queue

    HOST, PORT = host, port

    server = ThreadingTCPServer((HOST, PORT), TCPHandler)

    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    print('Network thread launched')

    try:
        raw_input()
        server.shutdown()
        server_thread.join()
    except KeyboardInterrupt as ki:
        # BUG: les thread en cours ne se terminent pas
        print("KeybordInterrupt: server shutdown")
        server.shutdown()
