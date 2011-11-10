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
COLUMNS = 32
ROWS = 24

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
        self.map = [[0 for col in xrange(32)] for row in xrange(24)]  # DEBUG: a map without blocking square
        f = open("../shared/village.collide", 'r')
        for i in xrange(ROWS):
            line = f.readline()[:-1]
            row = line.split(' ')
            for j in xrange(COLUMNS):
                self.map[i][j] = int(row[j])
        f.close()
        self.entities = {}
        self.entities_pos = {}
        self.factions = {}


    def load_fixtures(self):
        """
        Here is the place to define the entities which will be load on
        the field before the battle.
        """
        epouvantail = entity.Entity(id=1001, type='scarecrow', faction_id=2, hp=30)
        self.register(epouvantail, entity_id=1001, faction_id=2, x=16, y=21)

        arbre1 = entity.Entity(id=2001, type='tree', faction_id=0, hp=10)
        self.register(arbre1, entity_id=2001, faction_id=0, x=28, y=5)
        arbre2 = entity.Entity(id=2002, type='tree', faction_id=0, hp=10)
        self.register(arbre2, entity_id=2002, faction_id=0, x=29, y=12)
        arbre3 = entity.Entity(id=2003, type='tree', faction_id=0, hp=10)
        self.register(arbre3, entity_id=2003, faction_id=0, x=29, y=18)
        arbre4 = entity.Entity(id=2004, type='tree', faction_id=0, hp=10)
        self.register(arbre4, entity_id=2004, faction_id=0, x=20, y=21)
        arbre5 = entity.Entity(id=2005, type='tree', faction_id=0, hp=10)
        self.register(arbre5, entity_id=2005, faction_id=0, x=14, y=25)
        arbre6 = entity.Entity(id=2006, type='tree', faction_id=0, hp=10)
        self.register(arbre6, entity_id=2006, faction_id=0, x=6, y=20)
        arbre7 = entity.Entity(id=2007, type='tree', faction_id=0, hp=10)
        self.register(arbre7, entity_id=2007, faction_id=0, x=6, y=11)
        arbre8 = entity.Entity(id=2008, type='tree', faction_id=0, hp=10)
        self.register(arbre8, entity_id=2008, faction_id=0, x=8, y=5)
        arbre9 = entity.Entity(id=2009, type='tree', faction_id=0, hp=10)
        self.register(arbre9, entity_id=2009, faction_id=0, x=16, y=3)
        arbre10 = entity.Entity(id=2010, type='tree', faction_id=0, hp=10)
        self.register(arbre10, entity_id=2010, faction_id=0, x=22, y=5)
        arbre11 = entity.Entity(id=2011, type='tree', faction_id=0, hp=10)
        self.register(arbre11, entity_id=2011, faction_id=0, x=21, y=12)
        arbre12 = entity.Entity(id=2012, type='tree', faction_id=0, hp=10)
        self.register(arbre12, entity_id=2012, faction_id=0, x=13, y=14)

        house = entity.Entity(id=3000, type='house', faction_id=0, hp=500)
        self.register(house, entity_id=3000, faction_id=0, x=18, y=14)


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


    def faction_lost(self, faction_id):
        """
        Determine if a given faction has lost.

        Arguments:
        - `faction_id`: faction identifier.
        """
        lost = True
        for entity_id in self.factions[faction_id]:
            if not self.entities[entity_id].is_dead():
                lost = False

        return lost


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
        if len(self.map) <= y:
            result = True
        elif len(self.map[y]) <= x:
            result = True
        elif self.map[y][x] != FREE:
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
