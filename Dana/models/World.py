#!/usr/bin/env python
#-*- coding: utf-8 -*-

import random

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
        
        #TODO(tewfik): random for debug, change with config file reading
        self.map = [ [random.randint(0,1) for j in xrange(100)] for i in xrange(100) ]
        self.entities = []
        self.entities_pos = []


    def get_objet_by_position(self, position):
        """
        Get an object which is on a given position.
        
        Arguments:
        - `position`: tuple following the format (pos_x, pos_y)

        Return: an entity object.
        """
        #search stuff
        pass

    def get_position_by_object_id(self, id):
        """
        Retrieve the position of a given object.
        
        Arguments:
        - `id`: unique entity identifier.

        Return: position of the given entity. tuple (x, y).
        """
        #search stuff
        pass


    def register(self, entity):
        """
        An entity who join the world have to register to it.

        Arguments:
        - `entity`: a player, a monster, a vehicle ...
        """
        # TODO(tewfik): define a spawn area
        pos_x = 0
        pos_y = 0
        self.entities.append([pos_x, pos_y, entity])

    
    def unregister(self, entity_id):
        """
        Delete an entity from the world.

        Arguments:
        - `entity_id`: unique entity identifier.
        """
        pass

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
        if(self.get_object_by_position((x,y))):
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
