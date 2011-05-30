#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygame
from pygame.locals import *
from math import sqrt
from locales import *

class List():
    """
    An object used by the render engine to store every entities on the world.
    """

    def __init__(self):
        """
        Create the lists attributes:

        Attributes:
        - `entities`: internal list of entities.
        """
        self.entities = {}


    def get_layer(self, i):
        """
        Give a sub-dictionnary of entity of the given layer.

        Arguments:
        - `i`: number of the layer (0 is bottom layer, HEIGHT is top layer)
        """
        layer= {}
        for uid in self.entities:
            if self.entities[uid].pos[1] == i:
                layer[uid] = self.entities[uid]
        return layer


    def get_by_pos(self, pos):
        """
        """
        entity = None
        for uid in self.entities:
            if self.entities[uid].pos == pos:
                entity = self.entities[uid]
                break
        return entity


    def add_entity(self, pos, width, height, max_hp, hp, faction, uid, anim_path):
        """
        Create a new entity and store it in the list with is uid.

        Arguments:
        - `pos`: a (x, y) tuple with the starting coordinate.
        - `width`: the width of the entity.
        - `height`: the height of the entity.
        - `max_hp`: Gives the max hp of the entity.
        - `hp`: Gives the current hp of the entity.
        - `faction`: identify of the faction the entity belongs to.
        - `uid`: an unique identifier (int).
        - `animate_path`: the path to the .anim file of the entity.
        """
        self.entities[uid] = Entity(pos, width, height, max_hp, hp, faction)
        try:
            f = open("data/"+anim_path, 'r')
        except:
            print "Can't load data/"+anim_path
        for line in f.readlines():
            line = line.split("**")
            self.entities[uid].add_animation(line[0], line[3:-1], int(line[1]), line[2])
        f.close()


    def values(self):
        """
        """
        for entity in self.entities.values():
            yield entity


    def __iter__(self):
        """
        """
        return self.entities.__iter__()


    def __delitem__(self, uid):
        """
        Remove an entity to free its memory.

        Arguments:
        - `uid`: the unique id (int) of the entity to delete.
        """
        del self.entities[uid]


    def __getitem__(self, uid):
        """
        allow the user to get entity from the list with list_obj[uid].

        Arguments:
        - `uid`:  the uid of the entity we want to get.

        Return: An entity object from the list.
        """
        return self.entities[uid]


    def __setitem__(self, uid, entity):
        """
        Allow to create items with allocations.
        """
        self.add_entity(entity[0], entity[1], entity[2], entity[3], entity[4], entity[5], uid, entity[6])



class Entity():
    """
    Object representing any living or non-living entities on the world.
    """

    def __init__(self, pos, width, height, max_hp, hp, faction):
        """
        Set the starting position of the entity.

        Attributes:
        - `animations`: a list of Animation objects associated to the entity.
        - `pos`: a (x, y) tuple with the starting coordinate.
        - `width`: the width of the entity.
        - `height`: the height of the entity.
        - `max_hp`: Gives the max hp of the entity.
        - `hp`: Gives the current hp of the entity.
        - `alive`: A boolean setting if the entity is alive or dead.
        - `faction`: identify of the faction the entity belongs to.
        - `current_anim`: the current played animation.
        - `default_anim`: the animation to play by default.
        - `pixel_pos`: the current position (in pixels).
        - `dest`: the destination the entity is moving to ([x, y] in pixels).
        """
        self.animations = {}
        self.pos = pos
        self.width = width
        self.height = height
        self.max_hp = max_hp
        self.hp = hp
        self.alive = True
        self.faction = faction
        self.current_anim = "idle_down" # TODO(mika): initialize in a better way
        self.default_anim = "idle_down" # TODO(mika): initialize in a better way
        self.pixel_pos = ((pos[0] + 0.5)*SQUARE_SIZE - self.width / 2, (pos[1] + 1)*SQUARE_SIZE - self.height)
        self.dest = self.pixel_pos
        self.speed = 1  # TODO(mika): initialize in a better way


    def add_animation(self, name, sprites_paths, period, direction):
        """
        Add a new animation to the entity.

        Arguments:
        - `name`: name of the animation (ie: attack, idle...).
        - `sprites_paths`: list of paths to the sprites.
        - `period`: number of frame to wait between two sprites.
        - `direction`: the direction the entity is facing during the animation.
        """
        sprites = []
        for path in sprites_paths:
            sprite = pygame.image.load('sprites/'+path)
            sprites.append(sprite)
        self.animations[name] = Animation(name, sprites, period, direction)


    def die(self):
        """
        """
        self.alive = False
        if "idle_dead" in self.animations:
            self.play_anim("idle_dead", loop=True)


    def move(self, dest, speed):
        """
        Move the entity to a new location at a given speed.

        Arguments:
        - `dest`: a tuple (x, y) giving the destination's coordinates.
        - `speed`: movespeed in pixel per frame.
        """
        if (abs(dest[1] - self.pos[1]) >= abs(dest[0] - self.pos[0])):
            if dest[1] < self.pos[1]:
                self.play_anim('move_up', True)
            elif dest[1] > self.pos[1]:
                self.play_anim('move_down', True)
        else:
            if dest[0] > self.pos[0]:
                self.play_anim('move_right', True)
            elif dest[0] < self.pos[0]:
                self.play_anim('move_left', True)

        self.pos = dest
        self.dest = ((dest[0] + 0.5)*SQUARE_SIZE - self.width/2, (dest[1] + 1)*SQUARE_SIZE - self.height)

        self.speed = speed


    def update(self):
        """
        Give a timer's tick to the entity so it redraw itself and give an image to display to the world.

        Return: A pygame.Surface object.
        """
        if self.dest != self.pixel_pos:
            vect = (self.dest[0] - self.pixel_pos[0], self.dest[1] - self.pixel_pos[1])
            norm = sqrt(vect[0]**2 + vect[1]**2)
            vect = (self.speed * vect[0] / norm, self.speed * vect[1] / norm)
            oldpos = self.pixel_pos
            self.pixel_pos = (self.pixel_pos[0] + vect[0], self.pixel_pos[1] + vect[1])
            if (oldpos[0] < self.dest[0] < self.pixel_pos[0]) or (oldpos[0] > self.dest[0] > self.pixel_pos[0]):
                self.pixel_pos = (self.dest[0], self.pixel_pos[1])
            if (oldpos[1] < self.dest[1] < self.pixel_pos[1]) or (oldpos[1] > self.dest[1] > self.pixel_pos[1]):
                self.pixel_pos = (self.pixel_pos[0], self.dest[1])
            if (self.dest == self.pixel_pos):
                self.stop_anim()

        if self.animations[self.current_anim].end:
            self.play_anim(self.default_anim, True)
        return self.animations[self.current_anim].next_frame()


    def play_anim(self, name, loop):
        """
        Change the animation being played if given animation exists.

        Arguments:
        - `name`: the name of the animation to be played.
        - `loop`: True to play the anim in a loop, False to play once.
        """
        if name in self.animations:
            self.current_anim = name
            self.animations[name].reset(loop)


    def stop_anim(self):
        """
        Stop the current animation and play idle anim.
        """
        anim_idle = "idle_"+self.animations[self.current_anim].direction
        self.play_anim(anim_idle, True)


    def is_still_animated(self):
        """
        """
        if self.current_anim.startswith('idle'):
            return False
        else:
            return True



#TODO(Mika): add a sound effect for animation.
class Animation():
    """
    Use to manipulate an entity's animation.
    """

    def __init__(self, name, sprites, period, direction):
        """
        Initialize the animation.

        Attributes:
        - `name`: name of the animation (ie: attack, idle...).
        - `sprites`: list of sprites (pygame.image).
        - `period`: number of frame to wait between two sprites.
        - `frame_elapsed`: number of frame elapsed since the animation started.
        - `current_sprite`: the current displayed sprite.
        - `nb_sprites`: the number of sprites in the animation.
        - `end`: a boolean (True : ended, False : playing).
        - `loop`: True to play the anim in a loop, False to play once.
        - `direction`: the direction the entity is facing during the animation.
        """
        self.name = name
        self.sprites = sprites
        self.period = period
        self.frame_elapsed = 0
        self.current_sprite = 0
        self.nb_sprites = len(sprites)
        self.end = False
        self.loop = False
        self.direction = direction


    def reset(self, loop):
        """
        restart the animation.

        Arguments:
        - `loop`: True to play the anim in a loop, False to play once.
        """
        self.current_sprite = 0
        self.frame_elapsed = 0
        self.end = False
        self.loop = loop


    def next_frame(self):
        """
        Increase internal frame counter and current animation's frame.

        Return: A pygame.Surface object.
        """
        self.frame_elapsed += 1
        if self.frame_elapsed >= self.period:
            self.frame_elapsed = 0
            if self.current_sprite < self.nb_sprites - 1:
                self.current_sprite += 1
            elif self.loop:
                self.reset(True)
            else:
                self.end = True
        return self.sprites[self.current_sprite]
