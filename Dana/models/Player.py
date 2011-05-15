#!/usr/bin/env python
#-*- coding: utf-8 -*-

import Entity

class Player(Entity.LivingEntity):
    """
    A player
    """

    def __init__(self, id=None, hp=100, strength=0, intell=0, armor=0, mresist=0):
        """
        """
        Entity.LivingEntity.__init__(id, hp, strength, intell, armor, mresist)
