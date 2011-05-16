#!/usr/bin/env python
#-*- coding: utf-8 -*-

class Entity(object):
    """
    A player, a monster, a vehicle ...
    """

    def __init__(self, id=None, hp=100, armor=0, mresist=0):
        """
        Entity creation.

        Attributes:
        - `id`: object unique identifier. Default = random generation.
        - `hp`: the maximum and base health point of the entity, when it reachs 0 the entity die.
        - `armor`: reduce incoming physical damage (100 armor = 100% increased effective health).
        - `mresist`: reduce incoming magic damage (100 mresist = 100% increased effective health).
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
        Inflict damage to the entity after calcul of damage reduction.

        Attributes:
        - `normal`: Amount of normal damage inflicted before damage reduction.
        - `magic`: Amount of magic damage inflicted before damage reduction.
        - `true`: Amount of true damage inflicted.
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
        Entity creation.

        Attributes:
        - `id`: object unique identifier. Default = random generation.
        - `hp`: the maximum and base health point of the entity, when it reachs 0 the entity die.
        - `strength`: the strength of the entity (mainly used to improve physical damage dealt).
        - `intell`: the intelligence of the entity (mainly used to improve magic damage dealt).
        - `armor`: reduce incoming physical damage (100 armor = 100% increased effective health).
        """
        Entity.__init__(id, hp, mresist, armor)
        self.strength = strength
        self.intell = intell
        self.l_attacks = {}


    def add_attack(self, name, base=(0, 0, 0), ratioStr=(0, 0, 0), ratioInt=(0, 0, 0)):
        """
        Add a new attack to the Entity.

        Attributes:
        - `name`: internal name given to the attack.
        - `base`: a tuple (phys, mag, true) representing base damage of the attack.
        - `ratioStr`: a tuple (phys, mag, true) of the ratio of strength used for the attack.
        - `ratioInt`: a tuple (phys, mag, true) of the ratio of intell used for the attack.
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
        inflict damage to a target hit by this attack.

        Attributes:
        - `target`: the entity hit by the attack.
        """
        normal_dmg = self.ent.strength * self.rStr[0] + self.ent.intell * self.rInt[0] + self.base[0]
        magic_dmg = self.ent.strength * self.rStr[1] + self.ent.intell * self.rInt[1] + self.base[1]
        true_dmg = self.ent.strenght * self.rStr[2] + self.ent.intell * self.rInt[2] + self.base[2]
        target.get_dmg(normal_dmg, magic_dmg, true_dmg)
