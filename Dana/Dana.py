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

#from shared.astar import Astar
sys.path.append('../shared/')
from astar import Astar

# interval in seconds when players are able to choose their actions
ACTION_CHOICE_TIMEOUT = 30
# number of actions allowed for one player in one turn
NB_ACTIONS = 6
# interval in seconds after which Dana stops to wait clients
TIMEOUT = 10
# number of squares max that an entity is allowed to move
NB_SQUARE_MOVE_MAX = 5


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
    - `spectators_queues`: dictionary of spectators' queues. Format : spectators_queues[client_id] = Queue object.
    - `next_action_id`: unique identifier to allocate to the next actions.
    - `clients_config`: clients configuration item => clients_config['client_id'][item_name] = item_value.
    - `clients_actions`: actions choosen by each clients => clients_actions[client_id] = deque((action_id, action), ...).
    - `actions_effects`: effects of actions => action_effects[action_id] = 'EFFECT:%d:pa:id:type:target_id:nb_damage'
    - `move_flow`: details of move actions => move_flow[pa][client_id] = (dest_x, des_y).
    - `state`: state of the game (PLAYERS_CONNECTION | PLAYERS_CONNECTION_LOCK | ACTIONS_CHOICE | RENDER_FIGHT | WAIT_RENDER_OK).
    - `round`: round identifier. Start to zero and increment at each round.
    - `players_ready_event`: notice battle thread that all clients are ready.
    - `players_ready`: list of ready players.
    - `render_ok_list`: list of clients which have finished to render.
    - `render_ok_event`: notice battle thread that all clients have finished to render.
    - `choice_ok_list`: list of clients which have chose their actions.
    - `choice_ok_event`: notice battle thread that all clients have chose their actions.
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
        self.clients_config = {}
        self.spectators_queues = {}
        self.next_action_id = 1
        self.clients_actions = {}
        self.move_flow = []
        self.actions_effects = {}
        self.state = 'PLAYERS_CONNECTION'
        self.round = 0
        self.players_ready_event = threading.Event()
        self.players_ready = []
        self.render_ok_list = []
        self.render_ok_event = threading.Event()
        self.choice_ok_list = []
        self.choice_ok_event = threading.Event()


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

            elif msg_tab[0] == 'READY_TO_PLAY':
                self.ready_to_play_request(client_id)

            elif msg_tab[0] == 'GET_BATTLE_STATE':
                self.get_battle_state_request(client_id)

            elif msg_tab[0] == 'CONFIRM_CHOICE':
                self.choice_ok_request(client_id)

            elif msg_tab[0] == 'RENDER_OK':
                self.render_ok_request(client_id)

            elif msg_tab[0] == 'PING':
                self.ping_request(client_id, msg_tab[1])

            elif msg_tab[0] == 'SET':
                self.set_request(client_id, item_name=msg_tab[1], value=msg_tab[2])

            elif msg_tab[0] == 'CHAT_MSG':
                self.chat_msg(client_id, msg_tab[1])

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
        self.players_ready = []
        self.state = 'PLAYERS_CONNECTION'

        self.world.load_fixtures()

        self.players_ready_event.wait()
        self.players_ready_event.clear()


        # rounds loop
        battle_is_finished = False
        winner = 0
        while not battle_is_finished:
            # actions choice phase
            self.clear_clients_actions()
            self.state = 'ACTIONS_CHOICE'
            self.send_to_all('ROUND_START:' + str(self.round))

            # wait that clients finish to choose their actions
            self.choice_ok_event.wait(timeout=ACTION_CHOICE_TIMEOUT)
            self.choice_ok_event.clear()
            self.choice_ok_list = []

            # send actions to clients, they will display them.
            self.state = 'RENDER_FIGHT'
            self.send_to_all('END_CHOICE:' + str(self.round))
            time.sleep(1)  # let the time to display banner

            # render battle and send actions to display to clients
            self.render_battle()

            # ask to client to display the battle (display actions previously sent) 
            self.state = 'WAIT_RENDER_OK'
            self.send_to_all('RENDER:' + str(self.round))

            # wait clients finished to display the battle
            self.render_ok_event.wait(timeout=TIMEOUT)
            self.render_ok_event.clear()
            self.render_ok_list = []
            time.sleep(1)  # let the time to clients to display banners.

            self.round += 1

            battle_is_finished, winner = self.battle_is_finished()

        print("Battle is finished. Winner : %d" % winner)
        self.send_to_all('END_GAME:%d' % winner)


    def render_battle(self):
        """
        Render the battle based on actions choice that clients have previously done.
        """
        # precalculate clients movements
        self.render_move()

        for count_actions in xrange(NB_ACTIONS):
            # send all actions for a given action turn to the clients
            for client_id, client_actions in self.clients_actions.items():
                # if the client have to move or if he hasn't finished his movement
                try:
                    move = self.move_flow[count_actions][client_id]
                    x, y = move
                except KeyError as e:
                    move = (None, None)
                    print 'client n° %d has no move to do.' % client_id
                if move != (None, None):
                    action = "MOVE:{pa}:{id}:{x}:{y}".format(pa=count_actions, id=client_id, x=x, y=y)
                    print 'MOVE OK %s' % action
                    self.send_to_all(action)
                else:
                    try:
                        action_id, action = client_actions.popleft()
                        if action.startswith('MOVE'):
                            # move action have already been handled
                            pass
                        elif action.startswith('ATTACK'):
                            action = action % (count_actions)
                            self.send_to_all(action)
                            while len(self.actions_effects[action_id]) > 0:
                                effect = self.actions_effects[action_id].popleft()
                                self.send_to_all(effect % (count_actions))
                        else:
                            print 'WTF %s' % action
                            self.send_to_all(action)

                    except IndexError as e:
                        print(e)
                        print('|-> empty actions list for client')


    def get_move_actions(self):
        """
        Get the list of "move" actions.

        Returns: the list of (client_id, src_pos, dest_pos, pa_start)
                 where:
                     - client_id is the client identifier.
                     - src_pos is the tuple (x, y) which represent initial position before the move.
                     - dest_pos is the tuple (x, y) which represent the position where the entity want to go.
                     - pa_start is the action number where the move start.
        """
        move_actions = []
        for client_id, client_actions in self.clients_actions.items():
            for move_pa, (action_id, action) in enumerate(client_actions):
                if action.startswith('MOVE:'):
                    action_split = action.split(':')

                    client_pos = self.world.get_position_by_object_id(client_id)
                    client_dest = action_split[3], action_split[4]

                    move_actions.append((client_id, client_pos, client_dest, move_pa))

        return move_actions


    def render_move(self):
        """
        Simulate and execute all "move" actions and prepare the request to send to Etain.
        """
        # list of (client_id, src_pos, dest_pos, pa_start)
        # where:
        #   client_id is the client identifier.
        #   src_pos is the tuple (x, y) which represent initial position before the move.
        #   dest_pos is the tuple (x, y) which represent the position where the entity want to go.
        #   pa_start is the action number where the move start.
        move_actions = self.get_move_actions()

        # build move flow by actions number
        self.move_flow = []

        finished_move_actions = set()
        for pa in xrange(NB_ACTIONS):
            moves_by_pa = {}

            for move_id, move in enumerate(move_actions):
                str_client_id, str_src_pos, str_dest_pos, str_pa_start = move

                client_id = int(str_client_id)
                src_pos = self.world.get_position_by_object_id(client_id)
                # src_pos = (int(str_src_pos[0]), int(str_src_pos[1]))
                dest_pos = (int(str_dest_pos[0]), int(str_dest_pos[1]))
                pa_start = int(str_pa_start)
                # if the move has started and isn't finished, then calculate it

                if move_id not in finished_move_actions and pa_start <= pa:
                    # build A* arguments

                    # we need a world representation which show where
                    # the blocking squares are
                    #
                    # copy world representation
                    world_representation = []
                    for line in self.world.map:
                        line_clone = []
                        for item in line:
                            line_clone.append(item)
                        world_representation.append(line_clone)

                    # and add entity as blocking square
                    for entity_x, entity_y in self.world.entities_pos.values():
                        if entity_y <= len(world_representation) and entity_x <= len(world_representation[0]):
                            world_representation[entity_y][entity_x] = 1
                        else:
                            # ignore entity which are outside the screen
                            pass

                    free = [0]
                    block = [1]

                    # we have to re calculate the path to follow for
                    # each pa to be able to adapt the path to other
                    # entities' moves.
                    print 'A START MAGIC'
                    a_star_pos_list = Astar(world_representation, src_pos, dest_pos, free, block)
                    pos = a_star_pos_list[0]  # first move of one square
                    pos_x, pos_y = pos

                    # collision detection
                    if self.world.square_available(pos_x, pos_y):
                        print 'client n° %d move to (%d, %d)' % (client_id, pos_x, pos_y)
                        self.world.move(client_id, pos_x, pos_y)
                        # generate move action of 1 square
                        moves_by_pa[client_id] = (pos_x, pos_y)

                        if pos == dest_pos:  # is the move finished ?
                            print('move is finished')  #DEBUG
                            finished_move_actions.add(move_id)
                    else:
                        # collision detected
                        # generate "non-move" action
                        moves_by_pa[client_id] = (None, None)
                else:
                    print("move is finished or isn't started yet")
            # end for move in move_actions
            print('fin iteration PA : moves_by_pa = ', moves_by_pa)
            self.move_flow.append(moves_by_pa)
        # end for pa in range(NB_ACTIONS)
        print("move_flow", self.move_flow)


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

            #
            if self.state != 'PLAYERS_CONNECTION':
                # register the client as spectator
                self.spectators_queues[client_id] = msg
            else:
                self.clients_queues[client_id] = msg  # register the client queue
                self.clients_config[client_id] = {}

                player = models.entity.LivingEntity(id=client_id, type='warrior', faction_id=1 if client_id % 2 == 0 else 2)
                player.add_attack('attack', (20, 0, 0))
                player.add_attack('pyrotechnic', (0, 15, 0), max_range=5)
                player.add_attack('windblow', (0,0,0))
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
                    self.send_to_all('NEW_ENTITY:{type}:{faction}:{id}:{nickname}:{x}:{y}:{hpm}:{hp}'. \
                                         format(type=player.type,
                                                faction=player.faction_id,
                                                id=player.id,
                                                nickname=self.world.entities[player.id].nickname,
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


    def client_die(self, id, killer_id=0, action_id=0):
        """
        Register the death of a client.

        Arguments:
        - `id`: identifier of dead client.
        - `killer_id`: killer identifier.
        - `action_id`: id of action which killed the client.
        """
        print "client N° %d die" % id
        self.add_effect(action_id, killer_id, 'dead', id, 0)


    def client_is_dead(self, client_id):
        """
        Is a given client is dead ?

        Arguments:
        - `client_id`: client identifier.
        """
        return self.world.entities[client_id].is_dead()


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
        for spectator_queue in self.spectators_queues.values():
            spectator_queue.put(msg)


    def get_next_action_id(self):
        """
        Return the unique identifier to allocate to the next action.
        """
        next_action_id = self.next_action_id
        self.next_action_id += 1
        return next_action_id


    def clear_clients_actions(self):
        """
        Reinitialize to a void list all clients' actions lists.
        """
        self.next_action_id = 1
        self.clients_actions = {}
        self.actions_effects = {}
        for client_id in self.get_clients_ids():
            self.clients_actions[client_id] = collections.deque()


    def battle_is_finished(self):
        """
        Return: True if the battle is finished.
        """
        faction1_lost = self.world.faction_lost(1)
        faction2_lost = self.world.faction_lost(2)

        if not faction1_lost and faction2_lost:
            winner = 1
        elif faction1_lost and not faction2_lost:
            winner = 2
        else:
            winner = 0

        return (faction1_lost or faction2_lost), winner


    def ping_request(self, client_id, ping_id):
        """
        Answer 'pong' to a 'ping' request from the client.

        Arguments:
        - `client_id`: client who sent the request.
        - `ping_id`: identifier of the ping request (to differenciate several ping request).
        """
        self.clients_queues[client_id].put('PONG:%d' % ping_id)


    def set_request(self, client_id, item_name, value):
        """
        Initialize a configuration item for a given client.

        Arguments:
        - `client_id`: client identifier.
        - `item_name`: item name ('nickname').
        - `value`: item value, expected to be a str or an int.
        """
        if item_name == 'nickname':
            self.world.entities[client_id].set_nickname(value)
            self.send_to_all('SET:nickname:%d:%s' % (client_id, value))


    def chat_msg(self, client_id, msg):
        """
        Send a chat message to other clients.

        Arguments:
        - `client_id`: id of client which send the message.
        - `msg`: message to transmit to other clients.
        """
        self.send_to_all('CHAT_MSG:%d:%s' % (client_id, msg))


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
        entity = self.world.entities[client_id]
        response = 'ENTITY:%s:%d:%d:%s:%d:%d:%d:%d' % (type, faction_id, entity_id, entity.nickname, x, y, hp_max, hp)
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


    def ready_to_play_request(self, client_id):
        """
        A client notice that he is ready to play.

        Arguments:
        - `client_id`: client unique identifier
        """
        self.players_ready.append(client_id)

        if len(self.players_ready) == len(self.clients_queues):
            # lock connection to be sure that all connected clients are ready.
            self.state = 'PLAYERS_CONNECTION_LOCK'

        if len(self.players_ready) == len(self.clients_queues):
            self.players_ready_event.set()


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


    def choice_ok_request(self, client_id):
        """
        A clint notices that he has chosen its actions.

        Arguments:
        - `client_id`: client identifier
        """
        if self.state == 'ACTIONS_CHOICE':
            self.choice_ok_list.append(client_id)
            # if all clients have chosen, awake battle thread
            if len(self.choice_ok_list) == len(self.clients_queues):
                self.choice_ok_event.set()


    def add_effect(self, action_id, client_id, type, target_id, nb_dmg):
        """
        Associate an effect to an action.

        Arguments:
        - `action_id`: action's unique identifier.
        - `client_id`: client's unique identifier.
        - `type`: effect's type.
        - `target_id`: target identifier.
        - `nb_dmg`: number of damages.
        """
        if not self.actions_effects.has_key(action_id):
            self.actions_effects[action_id] = collections.deque()

        self.actions_effects[action_id].append('EFFECT:%d:{id}:{type}:{target_id}:{dmg}' \
                                                   .format(id=client_id, type=type, target_id=target_id, dmg=nb_dmg))


    def move_request(self, client_id, x, y):
        """
        An entity ask for move.

        The move action is recorded and all moves will be evaluated
        later dure the "render" phase in the self.render_move() method.

        Arguments:
        - `client_id`: client unique identifier.
        - `x`: x position
        - `y`: y position
        """
        if not self.client_is_dead(client_id) and self.world.distance_from_square(client_id, x, y) <= NB_SQUARE_MOVE_MAX:
            action_id = self.get_next_action_id()

            self.clients_actions[client_id].append((action_id, 'MOVE:%d:{id}:{x}:{y}'.format(id=client_id, x=x, y=y)))
            print 'client_position = (%d, %d)' % self.world.entities_pos[client_id] # DEBUG client position


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
        client = self.world.entities[client_id]
        if not client.is_dead() or target is not None:
            action_id = self.get_next_action_id()

            attack = self.world.entities[client_id].l_attacks[name]
            if self.world.distance_from_square(client_id, x, y) > attack.max_range:
                print("Client %d : square (%d, %d) out of range." % (client_id, x, y))
            else:
                target_is_dead, nb_dmg = attack.hit(target)

                self.clients_actions[client_id].append((action_id, 'ATTACK:%d:{id}:{name}:{x}:{y}'.format(id=client_id, name=name, x=x, y=y)))

                if name == 'windblow':
                    push_x, push_y = self.windblow_attack(client_id, target.id)
                    self.add_effect(action_id, client_id, 'push', target.id, str(push_x) + ':' + str(push_y))
                else:
                    self.add_effect(action_id, client_id, 'dmg', target.id, nb_dmg)

                if target_is_dead:
                    self.client_die(id=target.id, killer_id=client_id, action_id=action_id)
        # TODO(tewfik): manage attack fail


    def windblow_attack(self, attacker_id, target_id):
        """
        
        Arguments:
        - `attacker_id`:
        - `target_id`:
        """
        x_attacker, y_attacker = self.world.get_position_by_object_id(attacker_id)
        x_target, y_target = self.world.get_position_by_object_id(target_id)

        dest_square = (None, None)

        if x_attacker > x_target:
            # pousse a gauche
            if self.world.square_available(x_attacker - 2, y_attacker) and self.world.square_available(x_attacker - 3, y_attacker):
                dest_square = (x_target - 2, y_target)
        elif x_attacker < x_target:
            # pousse a droite
            if self.world.square_available(x_attacker + 2, y_attacker) and self.world.square_available(x_attacker + 3, y_attacker):
                dest_square = (x_target + 2, y_target)
        elif y_attacker > y_target:
            # pousse haut
            if self.world.square_available(x_attacker, y_attacker - 2) and self.world.square_available(x_attacker, y_attacker - 3):
                dest_square = (x_target, y_target - 2)
        else:
            # pousse bas
            if self.world.square_available(x_attacker, y_attacker + 2) and self.world.square_available(x_attacker, y_attacker + 3):
                dest_square = (x_target, y_target + 2)

        if dest_square == (None, None):
            dest_square = (x_target, y_target)
        else:
            self.world.move(target_id, dest_square[0], dest_square[1])

        return dest_square




def main(host, port):
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
    network.connection_start(dana_queue, host=host, port=port)

    dana.shutdown = True
    dana.join()
    print("Dana end")


if __name__ == '__main__':
    # command line argument management
    if(len(sys.argv) >= 3):
	    host = sys.argv[1]
	    port = int(sys.argv[2])
    elif(len(sys.argv) >= 2):
        host = 'localhost'
        port = int(sys.argv[1])
    else:
        host = 'localhost'
        port = 1337

    main(host, port)
