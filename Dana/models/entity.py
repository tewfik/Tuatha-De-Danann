#!/usr/bin/env python
#-*- coding: utf-8 -*-

class Entity(object):
    """
    A player, a monster, a vehicle ...
    """

    def __init__(self, id, type, faction_id=0, hp=100, armor=0, mresist=0):
        """
        Entity creation.

        Attributes:
        - `id`: object unique identifier. Default = random generation.
        - `type`: entity type ('scarecrow' | 'warrior')
        - `faction_id`: faction identifier.
        - `hp`: the current health point of the entity, when it reachs 0 the entity die.
        - `maxhp`: the maximum and base health point of the entity.
        - `armor`: reduce incoming physical damage (100 armor = 100% increased effective health).
        - `mresist`: reduce incoming magic damage (100 mresist = 100% increased effective health).
        """
        self.id = id
        self.type = type
        self.faction_id = faction_id
        self.hp = hp
        self.maxhp = hp
        self.armor = armor
        self.mresist = mresist


    def __getitem__(self, stat):
        """
        improved getter to easily access stats.

        Arguments:
        - `stat`: the name of the stat to get.

        Return: the value of the given stat.
        """
        if stat == 'hp':
            return self.hp
        elif stat == 'maxhp':
            return self.maxhp
        elif stat == 'mr':
            return self.mresist
        elif stat == 'armor':
            return self.armor


    def get_id(self):
        """
        Getter.
        """
        return self.id


    def get_dmg(self, normal, magic, true):
        """
        Inflict damage to the entity after calcul of damage reduction.

        Arguments:
        - `normal`: Amount of normal damage inflicted before damage reduction.
        - `magic`: Amount of magic damage inflicted before damage reduction.
        - `true`: Amount of true damage inflicted.

        Return : a tuple (bool, dmg) True if hp reachs 0, else False. dmg is the damage dealt
        """
        normal_mul = 100 / (100 + self.armor)
        magic_mul = 100 / (100 + self.mresist)
        dmg = true + normal * normal_mul + magic * magic_mul
        self.hp -= dmg
        dead = False
        if self.hp <= 0:
            self.hp = 0
            dead = True
        return (dead, dmg)


    def is_dead(self):
        """
        Return: true if the entity is dead, else false.
        """
        return self.hp < 0



class LivingEntity(Entity):
    """
    An entity which can move, attack...
    """

    def __init__(self, id, type, faction_id=0, hp=100, strength=0, intell=0, armor=0, mresist=0):
        """
        Entity creation.

        Attributes:
        - `id`: object unique identifier. Default = random generation.
        - `type`: entity type ('scarecrow' | 'warrior' | 'tree')
        - `faction_id`: faction_id identifier.
        - `hp`: the current health point of the entity, when it reachs 0 the entity die.
        - `maxhp`: the maximum and base health point of the entity.
        - `armor`: reduce incoming physical damage (100 armor = 100% increased effective health).
        - `mresist`: reduce incoming magic damage (100 mresist = 100% increased effective health).
        - `strength`: the strength of the entity (mainly used to improve physical damage dealt).
        - `intell`: the intelligence of the entity (mainly used to improve magic damage dealt).
        - `l_attacks`: list of Attack object the entity can use.
        """
        Entity.__init__(self, id, type, faction_id, hp, mresist, armor)
        self.strength = strength
        self.intell = intell
        self.l_attacks = {}


    def __getitem__(self, stat):
        """
        improved getter to easily access stats.

        Arguments:
        - `stat`: the name of the stat to get.

        Return: the value of the given stat.
        """
        if stat == 'str':
            return self.strength
        elif stat == 'int':
            return self.intell
        else:
            Entity.__getitem__(stat)


    def add_attack(self, name, base=(0, 0, 0), ratioStr=(0, 0, 0), ratioInt=(0, 0, 0)):
        """
        Add a new attack to the Entity.

        Arguments:
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

    def __init__(self, entity, base, ratioStr, ratioInt, max_range=1):
        """
        Initialize the propertie of the attack.

        Attributes:
        - `ent`: the entity which this attack belongs to.
        - `base`: a tuple (normal, magic, true) corresponding to the base dmg of the attack.
        - `rStr`: a tuple (normal, magic, true) corresponding to the ratio of strength for each dmg's type.
        - `rInt`: a tuple (normal, magic, true) corresponding to the raiot of intelligence for each dmg's type.
        - `range`: attack maximum range.
        """
        self.ent = entity
        self.base = base
        self.rStr = ratioStr
        self.rInt = ratioInt
        self.max_range = max_range


    def hit(self, target):
        """
        inflict damage to a target hit by this attack.

        Arguments:
        - `target`: the entity hit by the attack.

        Return: a boolean (True : the entity died, False : it's still alive).
        """
        normal_dmg = self.ent['str'] * self.rStr[0] + self.ent['int'] * self.rInt[0] + self.base[0]
        magic_dmg = self.ent['str'] * self.rStr[1] + self.ent['int'] * self.rInt[1] + self.base[1]
        true_dmg = self.ent['str'] * self.rStr[2] + self.ent['int'] * self.rInt[2] + self.base[2]
        return target.get_dmg(normal_dmg, magic_dmg, true_dmg)
