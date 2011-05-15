#!/usr/bin/env python
#-*- coding: utf-8 -*-

class Entity(object):
    """
    A player, a monster, a vehicle ...
    """

    def __init__(self, id=None):
        """
        Entity creation

        Arguments:
        - `id`: object unique identifier. Default = random generation.
        """
        self.id = id
        self.health


    def get_id(self):
        """
        Getter.
        """
        return self.id


    def get_dmg(self, amount, type):
        """
        """
        pass



class LivingEntity(Entity):
    """
    An entity which can move, attack...
    """

    def __init__(self, id=None):
        """
        """
        Entity.__init__(id)
