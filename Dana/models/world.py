#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sys
#import pickle
#sys.path.append("../../shared/")
#from area import Area

import entity

# square states
FREE = 0
BLOCK = 1

# exceptions
class ForbiddenMove(Exception):
    """
    Exception raised when a player try to perform a forbidden move.
    """
    pass


class World(object):
    """
    The world
    """

    def __init__(self):
        """
        World creation.

        Attributes:
        - `map`: Area object.
        - `entities`: list of entities object.
        - `entities_pos`: list of entities' positions [(x1, y1), (x2, y2) ...].
        - `factions`: dictionnary of factions {0:[id1, id2, id3], 1:[id4, id5], 2:[id6]}
        """
        # f_map = open('../../shared/etain.map', 'r')
        # self.map = pickle.load(f_map)
        # f_map.close()
        self.map = [[0 for col in xrange(32)] for row in xrange(24)]  # DEBUG: a map without blocking square
        self.entities = {}
        self.entities_pos = {}
        self.factions = {}


    def load_fixtures(self):
        """
        """
        epouvantail = entity.Entity(id=1001, type='scarecrow', faction_id=2)
        self.register(epouvantail, entity_id=1001, faction_id=2, x=16, y=21)

        arbre1 = entity.Entity(id=2001, type='tree', faction_id=0)
        self.register(arbre1, entity_id=2001, faction_id=0, x=23, y=15)
        arbre2 = entity.Entity(id=2002, type='tree', faction_id=0)
        self.register(arbre2, entity_id=2002, faction_id=0, x=8, y=18)


    def get_object_by_position(self, position):
        """
        Get an object which is on a given position.

        Arguments:
        - `position`: tuple following the format (x, y)

        Return: an entity object.
        """
        result = None
        for index in self.entities:
            if self.entities_pos[index] == position:
                result = self.entities[index]
                break
        return result


    def get_position_by_object_id(self, id):
        """
        Retrieve the position of a given object.

        Arguments:
        - `id`: unique entity identifier.

        Return: position of the given entity. tuple (x, y).
        """
        return self.entities_pos[id]


    def register(self, entity, entity_id, faction_id, x, y):
        """
        An entity who join the world have to register to it.

        Arguments:
        - `entity`: a player, a monster, a vehicle ...
        - `entity_id`: entity identifier.
        - `faction_id`: faction identifier.
        - `x`: x coordinate where to spawn the entity.
        - `y`: y coordinate.

        Exceptions:
        - `ForbiddenMove`: the square (x, y) is unavailable.
        """
        if self.square_available(x, y):
            self.entities[entity_id] = entity
            self.entities_pos[entity_id] = (x, y)
            self.add_entity_to_faction(faction_id, entity_id)
        else:
            raise ForbiddenMove('square (%d, %d) unavailable' % (x, y))


    def add_entity_to_faction(self, faction_id, entity_id):
        """
        Add a given entity in a given faction.

        Arguments:
        - `faction_id`: faction identifier.
        - `entity`: entity identifier.
        """
        if not self.factions.has_key(faction_id):
            self.factions[faction_id] = []
        self.factions[faction_id].append(entity_id)
        self.entities[entity_id].faction = faction_id


    def unregister(self, entity_id, faction_id=None):
        """
        Delete an entity from the world.

        Arguments:
        - `entity_id`: unique entity identifier.
        """
        del(self.entities[id])
        del(self.entities_pos[id])
        # remove entity from its faction
        if faction_id is not None:
            self.factions[faction_id].remove(entity_id)
        else:
            for faction in self.factions:
                if entity_id in faction:
                    faction.remove(entity_id)
                    break


    def square_available(self, x, y):
        """
        Check that an entity can move on a given square.

        Arguments:
        - `x`: abcisses.
        - `y`: ordonnees

        Return: true => free square, else false.
        """
        result = True

        # if square is not free
        if self.map[x][y] != FREE:
            result = False
        # if there is another entity on the square
        if self.get_object_by_position((x, y)):
            result = False

        return result


    def distance_from_square(self, entity_id, x, y):
        """
        Get the distance between an entity and a given saqure.

        Arguments:
        - `id`: entity identifier.
        - `x`: square x.
        - `y`: square y.

        Return: the distance in square (int).
        """
        entity_x, entity_y = self.get_position_by_object_id(entity_id)

        return abs(x - entity_x) + abs(y - entity_y)


    def move(self, id, dest_x, dest_y):
        """
        An entity ask to move.

        Arguments:
        - `id`: unique object identifier of the entity.
        - `dest_x`: destination's x.
        - `dest_y`: destination's y.
        """
        if self.square_available(dest_x, dest_y):
            self.entities_pos[id] = (dest_x, dest_y)
        else:
            raise ForbiddenMove('square (' + str(dest_x) + ', ' + str(dest_y) + ') unavailable')
