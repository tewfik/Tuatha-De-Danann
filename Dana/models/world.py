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
        """
        # f_map = open('../../shared/etain.map', 'r')
        # self.map = pickle.load(f_map)
        # f_map.close()
        self.map = [[0 for col in xrange(32)] for row in xrange(24)]  # DEBUG: a map without blocking square
        self.entities = {}
        self.entities_pos = {}


    def load_fixtures(self):
        """
        """
        epouvantail = entity(id=999)
        self.register(epouvantail, id=999, 16, 3)


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


    def register(self, entity, id, x, y):
        """
        An entity who join the world have to register to it.

        Arguments:
        - `entity`: a player, a monster, a vehicle ...
        - `x`: x coordinate where to spawn the entity.
        - `y`: y coordinate.
        """
        self.entities[id] = entity
        self.entities_pos[id] = (x, y)


    def unregister(self, entity_id):
        """
        Delete an entity from the world.

        Arguments:
        - `entity_id`: unique entity identifier.
        """
        del self.entities[id]
        del self.entities_pos[id]

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
        if self.map[x][y] not in FREE:
            result = False
        # if there is another entity on the square
        if self.get_object_by_position((x, y)):
            result = False

        return result


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
