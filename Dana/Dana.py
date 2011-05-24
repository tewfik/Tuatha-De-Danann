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

# interval in seconds when players are allowed to connect.
PLAYER_CONNECTION_TIME_INTERVAL = 20
# interval in seconds when players are able to choose their actions
CHOICE_TIME_INTERVAL = 5
# interval in seconds of one action
ACTION_TIME_INTERVAL = 2
# number of actions allowed for one player in one turn
NB_ACTIONS = 1
# interval in seconds after which Dana stops to wait clients
TIMEOUT = 10


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
    - `state`: state of the game (PLAYERS_CONNECTION | ACTIONS_CHOICE | RENDER_FIGHT | WAIT_RENDER_OK).
    - `round`: round identifier. Start to zero and increment at each round.
    - `render_ok_list`: list of clients which have finished to render.
    - `render_ok_event`: notice battle thread that all clients have finished to render.

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
        self.state = 'PLAYERS_CONNECTIONS'
        self.round = 0
        self.render_ok = []
        self.render_ok_event = threading.Event()


    def run(self):
        """
        Main loop of Dana.
        """
        battle_thread = threading.Thread(target=self.battle)
        battle_thread.daemon = True
        battle_thread.start()

        while not self.shutdown:
            # wait for a queue message
            print('Dana is waiting for client request')
            client_id, request_msg = self.queue.get() # TODO(tewfik) : change this for a non-blocking one and manage a timeout ?
            client_id = int(client_id)
            print('Client %d sent : "%s"' % (client_id, request_msg))
            self.process_message(client_id, request_msg)

        battle_thread.join()


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

            elif self.state == 'ACTIONS_CHOICE':
                # consider clients actions if and only if Dana is in choice state
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

            elif msg_tab[0] == 'GET_BATTLE_STATE':
                self.get_battle_state_request(client_id)

            elif msg_tab[0] == 'RENDER_OK':
                self.render_ok_request(client_id)

            elif msg_tab[0] == 'PING':
                self.ping_request(client_id, msg_tab[1])

            else:
                print('Unknown request.')
        else:
            # error
            print('error: a request from an unregistered client has been received')


    def battle(self):
        """
        Process a battle with all clients connected.

        This function describe the flow of a battle
        """
        self.world.load_fixtures()

        # wait for players connection
        time.sleep(PLAYER_CONNECTION_TIME_INTERVAL)

        # rounds loop
        while not self.battle_is_finished():
            # actions choice phase
            self.clear_clients_actions()
            self.state = 'ACTIONS_CHOICE'
            self.send_to_all('ROUND_START:' + str(self.round))
            time.sleep(CHOICE_TIME_INTERVAL)  # wait that clients finish to choose their actions

            # send actions to clients, they will display them.
            self.state = 'RENDER_FIGHT'
            self.send_to_all('END_CHOICE:' + str(self.round))

            # render battle and send actions to display to clients
            self.render_battle()

            # ask to client to display the battle (display actions previously sent) 
            self.state = 'WAIT_RENDER_OK'
            self.send_to_all('RENDER:' + str(self.round))

            # wait clients finished to display the battle
            self.render_ok_event.wait(timeout=TIMEOUT)
            self.render_ok_event.clear()
            self.render_ok_list = []

            self.round += 1

        self.send_to_all('BATTLE_END')


    def render_battle(self):
        """
        Render the battle based on actions choice that clients have previously done.
        """
        for count_actions in xrange(NB_ACTIONS):
            self.send_to_all('BEGIN_ACTION:' + str(count_actions))
            # send all actions for a given action turn to the clients
            for client_actions in self.clients_actions.values():
                try:
                    action = client_actions.popleft()

                    ###############################################################################################################
                    # TODO(tewfik): write a better
                    self.send_to_all(action)
                    time.sleep(ACTION_TIME_INTERVAL)
                    ###############################################################################################################

                except IndexError as e:
                    print(e)
                    print('|-> empty actions list for client')


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
            player = models.entity.LivingEntity(id=client_id, type='warrior', faction_id=1)
            player.add_attack('attack', (10, 0, 0))
            x = random.randint(10, 22)
            y = 22
            while not self.world.square_available(x, y):
                x = random.randint(10, 22)

            try:
                self.world.register(entity=player, entity_id=client_id, faction_id=1, x=x, y=y)

                # confirm the registration of the client's queue => send its client_id
                self.clients_queues[client_id].put(str(client_id))
                self.clients_queues[client_id].put('YOU:%d:%d' % (client_id, player.faction_id))
                print('client N° %d has been registered' % client_id)

                # inform all the clients that there is a new entity
                player_position = self.world.get_position_by_object_id(player.id)
                self.send_to_all('NEW_ENTITY:{type}:{faction}:{id}:{x}:{y}:{hpm}:{hp}'.format(type=player.type,
                                                                                              faction=player.faction_id,
                                                                                              id=player.id,
                                                                                              x=player_position[0],
                                                                                              y=player_position[1],
                                                                                              hpm=player.maxhp,
                                                                                              hp=player.hp))
            except ForbiddenMove as e:
                print(e)

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


    def get_entity_faction(self, entity_id):
        """
        Get the entity's faction id.

        Note that Entity objects have a 'faction' attribute which is
        faster O(1) if you only need to know the faction of a given
        object.

        Arguments:
        - `entity_id`: entity's identifier.
        """
        for faction_id, faction in self.factions.items():
            if entity_id in faction:
                return faction_id


    def send_to_all(self, msg):
        """
        Send a message to all clients.

        Arguments:
        - `msg`: message to send.
        """
        for client_queue in self.clients_queues.values():
            client_queue.put(msg)


    def clear_clients_actions(self):
        """
        Reinitialize to a void list all clients' actions lists.
        """
        self.clients_actions = {}
        for client_id in self.get_clients_ids():
            self.clients_actions[client_id] = collections.deque()


    def battle_is_finished(self):
        """
        Return: True if the battle is finished.
        """
        return False

    def ping_request(self, client_id, ping_id):
        """
        Answer 'pong' to a 'ping' request from the client.

        Arguments:
        - `client_id`: client who sent the request.
        - `ping_id`: identifier of the ping request (to differenciate several ping request).
        """
        self.clients_queues[client_id].put('PONG:%d' % ping_id)


    def get_battle_state_request(self, client_id):
        """
        Send the battle state to a givent client.

        Arguments:
        - `client_id`: client identifier.
        """
        self.clients_queues[client_id].put('BATTLE_STATE:%s:%d' % (self.state, self.round))


    def send_entity_response(self, client_id, type, faction_id, entity_id, x, y, hp_max, hp):
        """
        Send an entity's details to a given client.

        Arguments:
        - `type`: entity's type ('warrior', 'scarecrow' ...).
        - `faction_id`: faction identifier.
        - `entity_id`: entity unique identifier.
        - `x`: x position.
        - `y`: y position.
        - `hp_max`: maximum hp.
        - `hp`: current hp.
        """
        response = 'ENTITY:%s:%d:%d:%d:%d:%d:%d' % (type, faction_id, entity_id, x, y, hp_max, hp)
        self.clients_queues[client_id].put(response)


    def get_entities_request(self, client_id):
        """
        Send entities list details to a client.

        Arguments:
        - `client_id`: client identifier
        """
        for entity_id in self.world.entities:
            entity = self.world.entities[entity_id]
            pos = self.world.entities_pos[entity_id]
            self.send_entity_response(
                client_id=client_id,
                type=entity.type,
                faction_id=entity.faction_id,
                entity_id=entity_id,
                x=pos[0],
                y=pos[1],
                hp_max=entity.maxhp,
                hp=entity.hp
                )


    def render_ok_request(self, client_id):
        """
        A client notices that he finished to render the battle.

        Arguments:
        - `client_id`: identifier of the client which has finished to render the battle.
        """
        if self.state == 'WAIT_RENDER_OK':
            self.render_ok_list.append(client_id)
            # if all clients have finished to render, awake battle thread
            if len(self.render_ok_list) == len(self.clients_queues):
                self.render_ok_event.set()


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
            self.clients_actions[client_id].append('MOVE:%d:%d:%d' % (client_id, x, y))
            print 'client_position = (%d, %d)' % self.world.entities_pos[client_id] # DEBUG client position
        except models.world.ForbiddenMove as e:
            print(e)


    def attack_request(self, client_id, name, x, y):
        """
        An entity ask for attacking.

        Arguments:
        - `client_id`: client unique identifier.
        - `name`: attack name
        - `x`: target x pos.
        - `y`: target y pos.
        """
        target = self.world.get_object_by_position((x, y))
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
