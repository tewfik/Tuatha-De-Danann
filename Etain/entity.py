#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygame
from pygame.locals import *

class EntitiesList():
    """
    An object used by the render engine to store every entities on the world.
    """

    def __init__(self):
        """
        Create the lists attributes:
        """
        self.entities = {}


    def add_entity(self, pos, uid, anima_path):
        """
        Create a new entity and store it in the list with is uid.

        Attributes:
        - `pos`: a (x, y) tuple with the starting coordinate.
        - `uid`: an unique identifier (int).
        - `animate_path`: the path to the .anim file of the entity.
        """
        self.entities[str(uid)] = Entity(pos)
        try:
            f = open(anima_path, 'r')
            for line in f.readlines:
                line = line.split("**")
                self.entities[str(uid)].add_animation(line[0], line[2:], int(line[1]))
            f.close()
        except:
            print "Can't load "+animate_path



class Entity():
    """
    Object representing any living or non-living entities on the world.
    """

    def __init__(self, pos):
        """
        Set the starting position of the entity.

        Attributes:
        - `pos`: a (x, y) tuple with the starting coordinate.
        """
        self.animations = {}
        self.pos = [pos[0], pos[1]]
        self.current_anim = "idle"


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
            sprite = pygame.image.load('sprites/'path)
            sprites.append(sprite)
        self.animation[name] = animation(name, sprites, period)


    def update(self):
        """
        Give a timer's tick to the entity so it redraw itself and pass it to the world.
        """
        return self.animation[self.current_anim].nextframe()


    def play_anim(self, name):
        """
        Change the animation being played.

        Attributes:
        - `name`: the name of the animation to be played.
        """
        self.current_anim = name
        self.animation[self.curren_anim].reset()



class animation():
    """
    Use to manipulate an entity's animation.
    """

    def __init__(self, name, sprites, period):
        """
        Initialize the animation.

        Attributes:
        - `name`: name of the animation (ie: attack, idle...).
        - `sprites_paths`: list of paths to the sprites.
        - `period`: number of frame to wait between two sprites.
        """
        self.name = name
        self.sprites = sprites
        self.period = period
        self.frame_elapsed = 0
        self.current_sprite = 0


    def reset(self):
        """
        restart the animation.
        """
        self.current_frame = 0
        self.frame_elapsed = 0


    def next_frame(self):
        """
        Increase internal frame counter and current animation's frame.
        """
        self.frame_elapsed += 1
        if self.frame_elapsed >= period:
            self.frame_elapsed = 0
            self.current_sprite += 1
        return self.sprites[self.current_sprite]
