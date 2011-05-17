#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import time
import threading
import Queue
import collections
import random

import network
import models.world
import models.entity

# interval in seconds when players are able to choose their actions
CHOICE_TIME_INTERVAL = 20
# interval in seconds of one action
ACTION_TIME_INTERVAL = 2
# number of actions allowed for one player in one turn
NB_ACTIONS = 1

class Dana(threading.Thread):
    """
    Dana is the main object of the server.

    It manages game logic, events, it process clients requests, it
    generate the stuff which has to be sent to clients ...

    Attributes:
    - `world`: a representation of the world.
    - `shutdown`: if True => terminate Dana.
    - `queue`: queue Dana has to use to receive messages which are addressed to it.
    - `clients_queues`: dictionary of clients' queues. Format : clients_queues[client_id] = Queue object.
    - `clients_actions` : actions of one turn choosen by each clients.
    - `state`: state of the game (CHOICE | RENDER_FIGHT).
    """

    def __init__(self, queue):
        """Constructor

        Arguments:
        - `queue`: the queue Dana has to use to receive messages which are addressed to it.
        """
        threading.Thread.__init__(self)

        self.world = models.world.World()
        self.shutdown = False
        self.queue = queue
        self.clients_queues = {}
        self.clients_actions = {}
        self.state = 'BEGIN_FIGHT'


    def process_message(self, client_id, msg):
        """
        Process a given message.

        Arguments:
        - `client_id`: id of the client which sent the message.
        - `msg`: message to process.
        """
        if client_id == 0:
            client_id = self.register_client(msg)
            print('Client n° %d has been registered' % client_id)

        # check that the client id is registered
        elif self.clients_queues.has_key(client_id):
            # request processing
            msg_tab = msg.split(':')
            if msg_tab[0] == 'GET_ENTITIES':
                self.get_entities_request(client_id)
            elif self.state = 'CHOICE':
                if msg_tab[0] == 'MOVE':
                    try:
                        self.move_request(client_id, x=int(msg_tab[1]), y=int(msg_tab[2]))
                    except ValueError as e:
                        print(e)
                elif msg_tab[0] == 'ATTACK':
                    try:
                        self.attack_request(client_id, name=msg_tab[1], x=int(msg_tab[2]), y=int(msg_tab[3]))
                    except ValueError as e:
                        print(e)
            else:
                print('Unknown request.')
        else:
            # error
            print('error: a request from an unregistered client has been received')


    def register_client(self, msg):
        """
        Register a client which ask for connection in Dana.

        Arguments:
        - `msg`: the first message of a client has to be a Queue that Dana will use to send data to the client.

        Return: client id which has been allocated to the client.
        """
        # check that the message is a Queue
        if msg.__class__.__name__ == Queue.Queue.__name__:
            client_id = self.get_next_id()        # generate an available client id.
            self.clients_queues[client_id] = msg  # register the client queue

            #
            player = models.entity.LivingEntity(id=client_id)
            player.add_attack('attack', (10, 0, 0))
            x = random.randint(10, 22)
            y = 22
            while not self.world.square_available(x, y):
                x = random.randInt(10, 22)

            self.world.register(player, client_id, x, y)
            # confirm the registration of the client's queue => send its client_id
            self.clients_queues[client_id].put(str(client_id))
            self.clients_queues[client_id].put('YOU:' + str(client_id))
        else:
            # error TODO(tewfik): create a ProtocolException
            print('protocol error: the first message send by a client thread to Dana'
                  'have to be a Queue reference.')

        return client_id


    def get_next_id(self):
        """
        Search the next available client identifier.

        TODO(tewfik): This method book the next available client identifier and return it.
        This identifier should be unique.

        Return: (int) the client identifier which can be allocated to the next client.
        """
        next_client_id = 1
        #lock self.next_client_id_search
        while self.clients_queues.has_key(next_client_id):
            next_client_id += 1
            #book next_client_id
        #unlock self.next_client_id_search
        print "next_client_id : " , next_client_id

        return next_client_id


    def free_booked_id(self, client_id):
        """
        Cancel the booking of a given client id.

        Arguments:
        - `client_id`: client_id to unbook.
        """
        pass


    def get_clients_ids(self):
        """
        Return: list of connected clients' ids.
        """
        return self.clients_queues.keys()


    def send_to_all(self, msg):
        """
        Send a message to all clients.

        Arguments:
        - `msg`: message to send.
        """
        for client_queue in self.clients_queues:
            client_queue.put(msg)


    def battle(self):
        """
        Process a battle with all clients connected.

        This function describe the flow of a battle
        """
        self.world.load_fixtures()

        battle_is_finished = False
        count_round = 0
        # rounds loop
        while not battle_is_finished:
            # actions choice phase
            self.state = 'CHOICE'
            self.clear_clients_actions()
            self.send_to_all('ROUND_START:' + str(count_round))
            time.sleep(CHOICE_TIME_INTERVAL)  # wait that clients finish to choose their actions

            # send actions to clients, they will display them.
            self.state = 'RENDER_FIGHT'
            for count_actions in xrange(NB_ACTION):
                self.send_to_all('BEGIN_ACTION:' + count_actions)
                # send all actions for a given action turn to the clients
                for client_actions in self.clients_actions:
                    action = client_actions.popleft()
                    self.send_to_all(action)
                    time.sleep(ACTION_TIME_INTERVAL)
                self.send_to_all('END_ROUND:' + str(count_round))
                count_round += 1

            if self.battle_is_finished():
                battle_is_finished = True

        self.send_to_all('BATTLE_END')


    def clear_clients_actions(self):
        """
        Reinitialize to a void list all clients' actions lists.
        """
        self.clients_actions = {}
        for client_id in self.get_clients_ids():
            self.clients_actions[client_id] = deque()


    def battle_is_finished(self):
        """
        Return: True if the battle is finished.
        """
        return False

    def run(self):
        """
        Main loop of Dana.
        """
        while not self.shutdown:
            # wait for a queue message
            print('Dana is waiting for client request')
            client_id, request_msg = self.queue.get() # TODO(tewfik) : change this for a non-blocking one and manage a timeout ?
            client_id = int(client_id)
            print('Client %d sent : "%s"' % (client_id, request_msg))
            self.process_message(client_id, request_msg)


    def get_entities_request(self, client_id):
        """
        Send entities list details to a client.

        Arguments:
        - `client_id`: client identifier
        """
        for entity_id in self.world.entities:
            entity = self.world.entities[entity_id]
            pos = self.world.entities_pos[entity_id]
            self.clients_queues[client_id].put('ENTITY:' + entity.type + ':' + entity_id + ':' + pos[0] + ':' + pos[1])


    def move_request(self, client_id, x, y):
        """
        An entity ask for move.

        Arguments:
        - `client_id`: client unique identifier.
        - `x`: x position
        - `y`: y position
        """
        #TODO(tewfik): check that the client don't move more than which he is allowed to move.
        try:
            self.world.move(client_id, x, y)
        except ForbidenMove as e:
            print(e)

        self.clients_actions[client_id].append('MOVE:%d:%d:%d' % (client_id, x, y))


    def attack_request(self, client_id, name, x, y):
        """
        An entity ask for attacking.

        Arguments:
        - `client_id`: client unique identifier.
        - `name`: attack name
        - `x`: target x pos.
        - `y`: target y pos.
        """
        target = self.world.get_objet_by_position((x, y))
        if target is not None:
            self.world.entities[client_id].l_attacks[name].hit(target)
            self.clients_actions[client_id].append('ATTACK:%d:%s:%d:%d' % (client_id, name, x, y))
        # TODO(tewfik): manage attack fail



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
    print("Dana end")


if __name__ == '__main__':
    # command line argument management
    if(len(sys.argv) >= 2):
        port = int(sys.argv[1])
    else:
        port = 1337

    main(port)
