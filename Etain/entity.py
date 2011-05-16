#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygame
from pygame.locals import *

class List():
    """
    An object used by the render engine to store every entities on the world.
    """

    def __init__(self):
        """
        Create the lists attributes:
        """
        self.entities = {}


    def __getitem__(self, uid):
        """
        allow the user to get entity from the list with list_obj[uid].
        """
        return self.entities[uid]


    def add_entity(self, pos, width, height, uid, anim_path):
        """
        Create a new entity and store it in the list with is uid.

        Attributes:
        - `pos`: a (x, y) tuple with the starting coordinate.
        - `width`: the width of the entity.
        - `height`: the height of the entity.
        - `uid`: an unique identifier (int).
        - `animate_path`: the path to the .anim file of the entity.
        """
        self.entities[uid] = Entity(pos, width, height)
        try:
            f = open("data/"+anim_path, 'r')
        except:
            print "Can't load data/"+anim_path
        for line in f.readlines():
            line = line.split("**")
            self.entities[uid].add_animation(line[0], line[2:-1], int(line[1]))
        f.close()


    def __delitem__(self, uid):
        """
        Remove an entity to free its memory.

        Attributes:
        - `uid`: the unique id (int) of the entity to delete.
        """
        del self.entities[uid]



class Entity():
    """
    Object representing any living or non-living entities on the world.
    """

    def __init__(self, pos, width, height):
        """
        Set the starting position of the entity.

        Attributes:
        - `pos`: a (x, y) tuple with the starting coordinate.
        - `width`: the width of the entity.
        - `height`: the height of the entity.
        """
        self.animations = {}
        self.pos = [pos[0], pos[1]]
        self.width = width
        self.height = height
        self.current_anim = "idle"
        self.default_anim = "idle"
        self.dest = [pos[0], pos[1]]


    def get_hitbox(self):
        """
        Return a pygame.Rect corresponding to the sprites size and the entity position.
        """
        return pygame.Rect(self.pos[0], self.pos[1], self.width, self.height)


    def add_animation(self, name, sprites_paths, period):
        """
        Add a new animation to the entity.

        Attributes:
        - `name`: name of the animation (ie: attack, idle...).
        - `sprites_paths`: list of paths to the sprites.
        - `period`: number of frame to wait between two sprites.
        """
        sprites = []
        for path in sprites_paths:
            sprite = pygame.image.load('sprites/'+path)
            sprites.append(sprite)
        self.animations[name] = Animation(name, sprites, period)

    def move(self, pos, speed):
        """
        Move the entity to a new location at a given speed.

        Attributes:
        - `pos`: a tuple (x, y) giving the destination's coordinates.
        - `speed`: movespeed in pixel per frame.
        """
        self.dest = [pos[0], pos[1]]
        self.speed = speed


    def update(self):
        """
        Give a timer's tick to the entity so it redraw itself and pass it to the world.
        """
        if self.dest != self.pos:
            vect = (self.dest[0] - self.pos[0], self.dest[1] - self.pos[1])
            norm = sqrt(vect[0]**2 + vect[1]**2)
            vect = (speed * vect[0] / norm, speed * vect[1] / norm)
            oldpos = pos
            self.pos = [self.pos[0] + vect[0], self.pos[1] + vect[1]]
            if (oldpos[0] < self.dest[0] < self.pos[0]) or (oldpos[0] > self.dest[0] > self.pos[0]):
                self.pos[0] = self.dest[0]
            if (oldpos[1] < self.dest[1] < self.pos[1]) or (oldpos[1] > self.dest[1] > self.pos[1]):
                self.pos[1] = self.dest[1]

        if self.animations[self.current_anim].end:
            self.play_anim(self.default_anim)
        return self.animations[self.current_anim].next_frame()


    def play_anim(self, name):
        """
        Change the animation being played.

        Attributes:
        - `name`: the name of the animation to be played.
        """
        self.current_anim = name
        self.animations[self.current_anim].reset()


#TODO(Mika): add a sound effect for animation.
class Animation():
    """
    Use to manipulate an entity's animation.
    """

    def __init__(self, name, sprites, period):
        """
        Initialize the animation.

        Attributes:
        - `name`: name of the animation (ie: attack, idle...).
        - `sprites`: list of sprites (pygame.image).
        - `period`: number of frame to wait between two sprites.
        """
        self.name = name
        self.sprites = sprites
        self.period = period
        self.frame_elapsed = 0
        self.current_sprite = 0
        self.nb_sprites = len(sprites)
        self.end = False


    def reset(self):
        """
        restart the animation.
        """
        self.current_sprite = 0
        self.frame_elapsed = 0
        self.end = False


    def next_frame(self):
        """
        Increase internal frame counter and current animation's frame.
        """
        self.frame_elapsed += 1
        if self.frame_elapsed >= self.period:
            self.frame_elapsed = 0
            if self.current_sprite < self.nb_sprites - 1:
                self.current_sprite += 1
            else:
                self.end = True
        return self.sprites[self.current_sprite]
