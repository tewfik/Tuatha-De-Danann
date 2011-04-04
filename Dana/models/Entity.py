#!/usr/bin/env python
#-*- coding: utf-8 -*-

class Entity(object):
    """A player, a monster, a vehicle ...
    """
    
    def __init__(self, id=null):
        """
        Entity creation
        
        Arguments:
        - `id`: object unique identifier. Default = random generation.
        """
        self.id = id

    def get_id(self):
        """Getter.
        """
        return self.id
