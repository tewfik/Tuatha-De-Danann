#!/usr/bin/env python
# -*- coding: UTF8 -*-

import sys
import SocketServer

class ThreadingTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer): pass


class TCPHandler(SocketServer.BaseRequestHandler):
    """
    """

    def register_query(self):
        """
        A client ask for an unique identifier.
        The server has to register the client id, his login and his (hashed) pass.
        """
        #get login/pass
        #client_id = AccountManagement.get_next_client_id()
        #send(client_id)
        pass


    def send_loop(self, client_id):
        """
        Dana send data to the client.
        """
        # main loop
        while True:
            # wait for a Queue event
            ##
            # send a client request
            self.request.send(data.upper())
            # wait for confirmation
            data = self.request.recv(1024).strip()
            # response management


    def receive_loop(self, client_id):
        """
        Dana receives data from the client, parses it and reacts to it.
        """
        # main loop
        while True:
            # wait for request
            data = self.request.recv(1024).strip()
            print "%s wrote: %s" % (self.client_address[0], data)

            try:
                response = controller_stuff(self.data)
            except(ValueError):
                response = 'vtff' # le signaler au client

            self.request.send(response)


    def handle(self):
        """
        Handle requests and allocate them to the concerned handle function.
        => register function : client connexion and identifier attribution
        => send_loop function : server send data to client
        => receive_loop funciton : server receive data from the client and reacts.
        """
        #TODO(tewfik): gérer la connexion des clients (login/pass)

        # choose between send connection and receive connection
        data = self.request.recv(1024).strip()
        connection_type, client_id = data.split(" ")

        if connection_type  == "send":
            self.send_loop(client_id)
        elif connection_type == "receive":
            self.receive_loop(client_id)
        else:
            self.request.send("vtff")


def main(port):
    """
    Main program.

    Attributes:
    - `port`: port which Dana listen.
    """
    HOST, PORT = 'localhost', port

    server = ThreadingTCPServer((HOST, PORT), TCPHandler)
    server.serve_forever()


if __name__ == '__main__':
    # command line argument management
    if(len(sys.argv) >= 2):
        port = int(sys.argv[1])
    else:
        port = 1337

    main(port)
