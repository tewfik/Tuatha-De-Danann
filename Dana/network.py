#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import threading
import SocketServer

# last client identifier which was allocated.
last_id = 0

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
        global last_id
        last_id += 1
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
        # main loop
        close_connection = False
        while not close_connection:
            # wait for a Queue event
            # TODO(tewfik): complete

            # send a client request
            try:
                self.request.send("coucou from server")
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
        # main loop
        while True:
            # wait for request
            try:
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
            print "%s wrote: %s" % (self.client_address[0], data)


    def handle(self):
        """
        Handle requests and allocate them to the concerned handle function.
        => register function : client connection and identifier attribution
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
        elif connection_type == "register":
            self.register()
        else:
            self.request.send("vtff")


    def end_connection(self):
        """
        """
        pass



def connection_start(port, host='localhost'):
    """
    Main program.

    Attributes:
    - `host`: host
    - `port`: port which Dana listen.
    """
    HOST, PORT = host, port

    server = ThreadingTCPServer((HOST, PORT), TCPHandler)

    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    try:
        raw_input()
        server.shutdown()
        server_thread.join()
    except KeyboardInterrupt as ki:
        # BUG: les thread en cours ne se terminent pas
        print "KeybordInterrupt: server shutdown"
        server.shutdown()
