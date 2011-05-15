#!/usr/bin/env python
#-*- coding: utf-8 -*-

class Entity(object):
    """
    A player, a monster, a vehicle ...
    """

    def __init__(self, id=None, hp=100, armor=0, mresist=0):
        """
        Entity creation

        Arguments:
        - `id`: object unique identifier. Default = random generation.
        """
        self.id = id
        self.health = hp
        self.mresist = mresist
        self.armor = armor


    def get_id(self):
        """
        Getter.
        """
        return self.id


    def get_dmg(self, normal, magic, true):
        """
        """
        normal_mul = 100 / (100 + self.armor)
        magic_mul = 100 / (100 + self.mresist)
        self.health -= true + normal * normal_mul + magic * magic_mul
        if self.health < 0:
            self.health = 0



class LivingEntity(Entity):
    """
    An entity which can move, attack...
    """

    def __init__(self, id=None, hp=100, strength=0, intell=0, armor=0, mresist=0):
        """
        """
        Entity.__init__(id, hp, mresist, armor)
        self.strength = strength
        self.intell = intell
        self.l_attacks = {}


    def add_attack(self, name, base=(0, 0, 0), ratioStr=(0, 0, 0), ratioInt=(0, 0, 0)):
        """
        Add a new attack to the Entity.
        """
        self.l_attacks[name] = Attack(self, base, ratioStr, ratioInt)



class Attack():
    """
    Represent an attack of an entity.
    """

    def __init(self, entity, base, ratioStr, ratioInt):
        """
        Initialize the propertie of the attack.

        Attributes:
        - `entity`: the entity which this attack belongs to.
        - `base`: a tuple (normal, magic, true) corresponding to the base dmg of the attack.
        - `ratioStr`: a tuple (normal, magic, true) corresponding to the ratio of strength for each dmg's type.
        - `ratioInt`: a tuple (normal, magic, true) corresponding to the raiot of intelligence for each dmg's type.
        """
        self.ent = entity
        self.base = base
        self.rStr = ratioStr
        self.rInt = ratioInt


    def hit(self, target):
        """
        """
        normal_dmg = self.ent.strength * self.rStr[0] + self.ent.intell * self.rInt[0] + self.base[0]
        magic_dmg = self.ent.strength * self.rStr[1] + self.ent.intell * self.rInt[1] + self.base[1]
        true_dmg = self.ent.strenght * self.rStr[2] + self.ent.intell * self.rInt[2] + self.base[2]
        target.get_dmg(normal_dmg, magic_dmg, true_dmg)
