#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import threading
import Queue

import network

class Dana(threading.Thread):
    """
    Dana is the main object of the server.

    It manages game logic, events, it process clients requests, it
    generate the stuff which has to be sent to clients ...

    Attributes:
    - `shutdown`: if True => terminate Dana
    - `queue`: queue Dana has to use to receive messages which are addressed to it.
    - `clients_queues`: dictionary of clients' queues. Format : clients_queues[client_id] = Queue object.
    """

    def __init__(self, queue):
        """Constructor

        Arguments:
        - `queue`: the queue Dana has to use to receive messages which are addressed to it.
        """
        threading.Thread.__init__(self)

        self.shutdown = False
        self.queue = queue
        self.clients_queues = {}


    def process_message(self, client_id, msg):
        """
        Process a given message.

        Arguments:
        - `client_id`: id of the client which sent the message.
        - `msg`: message to process.
        """
        if client_id == 0:
            self.register_client(msg)
        # check that the client id is registered
        elif self.clients_queues.has_key(client_id):
            # request processing
            client_id, method = msg.split(':')
            self.clients_queues[client_id].put('coucou %s' % client_id)  # DEBUG
        else:
            # error
            print('error: a request from an unregistered client has been received')


    def register_client(self, msg):
        """
        Register a client which ask for connection in Dana.

        Arguments:
        - `client_id`: client unique identifier
        - `msg`: the first message of a client has to be a Queue that Dana will use to send data to the client
        """
        # check that the message is a Queue
        if msg.__class__.__name__ == Queue.Queue.__name__:
            client_id = self.get_next_id()        # generate an available client id.
            self.clients_queues[client_id] = msg  # register the client queue

            # confirm the registration of the client's queue => send its client_id
            self.clients_queues[client_id].put(client_id)
        else:
            # error
            print('protocol error: the first message send by a client thread to Dana'
                  'have to be a Queue reference.')


    def get_next_id(self):
        """
        Search the next available client identifier.

        TODO(tewfik): This method book the next available client identifier and return it.
        This identifier should be unique.

        Return: (int) the client identifier which can be allocated to the next client.
        """
        next_client_id = 1
        #lock self.next_client_id_search
        while(self.clients_queues[next_client_id] is not None):
            next_client_id += 1
            #book next_client_id
        #unlock self.next_client_id_search

        return next_client_id


    def free_booked_id(self, client_id):
        """
        Cancel the booking of a given client id.

        Arguments:
        - `client_id`: client_id to unbook.
        """
        pass


    def run(self):
        """
        Main loop of Dana.
        """
        while not self.shutdown:
            # wait for a queue message
            client_id, request_msg = self.queue.get() # TODO(tewfik) : change this for a non-blocking one and manage a timeout ?
            self.process_message(client_id, request_msg)
            


def main(port):
    """Main program.

    Arguments:
    - `port`: listenning port
    """
    # initiate the main queue used by client-connected thread to send data to the
    # main server thread.
    dana_queue = Queue.Queue()

    # launch the main Dana loop in a separate thread
    dana = Dana(dana_queue)
    dana.start()
    print('Dana thread launched')

    # launch network listnening (blocking call waiting for stopping of the network engine)
    network.connection_start(dana_queue, port=port)

    dana.shutdown = True
    dana.join()


if __name__ == '__main__':
    # command line argument management
    if(len(sys.argv) >= 2):
        port = int(sys.argv[1])
    else:
        port = 1337

    main(port)
