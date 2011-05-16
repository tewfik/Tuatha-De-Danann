#!/usr/bin/env python
#-*- coding: utf-8 -*-

import pickle
import sys
sys.path.append("../../shared/")
from area import Area


# square states
FREE = 0
BLOCK = 1

# exceptions
class ForbiddenMove(Exception):
    """
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
        - `map`: main array.
        - `entities`: A list which represent entities' positions which can behave in the world. A list following the format [(pos_x1, pos_y1), ...]
        - `entitites_pos`: Represent entities [object1, ...].
        """
        f_map = open('../../shared/etain.map')
        self.map = pickle.load(f_map)
        f_map.close()
        self.entities = {}
        self.entities_pos = {}


    def get_objet_by_position(self, position):
        """
        Get an object which is on a given position.

        Arguments:
        - `position`: tuple following the format (pos_x, pos_y)

        Return: an entity object.
        """
        for index in self.entities:
            if self.entities_pos[index] = [position[0], position[1]]:
                i = index
                break
        return self.entities[i]


    def get_position_by_object_id(self, id):
        """
        Retrieve the position of a given object.

        Arguments:
        - `id`: unique entity identifier.

        Return: position of the given entity. tuple (x, y).
        """
        return self.entities_pos[id]


    def register(self, entity, id):
        """
        An entity who join the world have to register to it.

        Arguments:
        - `entity`: a player, a monster, a vehicle ...
        """
        # TODO(tewfik): define a spawn area
        pos_x = 0
        pos_y = 0
        self.entities[id] = entity
        self.entities_pos[id] = [pos_x, pos_y]


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
        result = true

        # if square is not free
        if(self.map[x][y] != FREE):
            result = false
        # if there is another entity on the square
        if(self.get_object_by_position((x, y))):
            result = false

        return result

    def move(self, id, dest_x, dest_y):
        """
        An entity ask to move.

        Arguments:
        - `id`: unique object identifier of the entity.
        - `dest_x`: destination's x.
        - `dest_y`: destination's y.
        """
        if(self.square_available(dest_x, dest_y)):
            #register
            #confirm
            pass
