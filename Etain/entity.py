#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygame
from pygame.locals import *
from math import sqrt

SQUARE_SIZE = 32

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


    def __getitem__(self, uid):
        """
        allow the user to get entity from the list with list_obj[uid].

        Arguments:
        - `uid`:  the uid of the entity we want to get.

        Return: An entity object from the list.
        """
        return self.entities[uid]


    def add_entity(self, pos, width, height, hp, uid, anim_path):
        """
        Create a new entity and store it in the list with is uid.

        Arguments:
        - `pos`: a (x, y) tuple with the starting coordinate.
        - `width`: the width of the entity.
        - `height`: the height of the entity.
        - `hp`: Gives the current hp and max hp of the entity.
        - `uid`: an unique identifier (int).
        - `animate_path`: the path to the .anim file of the entity.
        """
        self.entities[uid] = Entity(pos, width, height, hp)
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

        Arguments:
        - `uid`: the unique id (int) of the entity to delete.
        """
        del self.entities[uid]



class Entity():
    """
    Object representing any living or non-living entities on the world.
    """

    def __init__(self, pos, width, height, hp):
        """
        Set the starting position of the entity.

        Attributes:
        - `animations`: a list of Animation objects associated to the entity.
        - `pos`: a (x, y) tuple with the starting coordinate.
        - `width`: the width of the entity.
        - `height`: the height of the entity.
        - `hp`: Gives the current hp of the entity.
        - `max_hp`: Gives the max hp of the entity.
        - `faction_color`: Color of the entity's faction.
        - `current_anim`: the current played animation.
        - `default_anim`: the animation to play by default.
        - `cur_pos`: the current position (in pixels).
        - `dest`: the destination the entity is moving to ([x, y] in pixels).
        """
        self.animations = {}
        self.pos = [pos[0], pos[1]]
        self.width = width
        self.height = height
        self.hp = hp
        self.max_hp = hp
        self.faction_color = (0, 0, 150)
        self.current_anim = "idle"
        self.default_anim = "idle"
        self.cur_pos = [(pos[0] + 1)*SQUARE_SIZE - self.width, (pos[1] + 1)*SQUARE_SIZE - self.height]
        self.dest = self.cur_pos
        self.speed = 1  # TODO(mika): initialize in a better way


    def get_hitbox(self):
        """
        Get the hitbox corresponding to the sprites size and the entity position.

        Return: a pygame.Rect.
        """
        return pygame.Rect(self.cur_pos[0], self.cur_pos[1], self.width, self.height)


    def add_animation(self, name, sprites_paths, period):
        """
        Add a new animation to the entity.

        Arguments:
        - `name`: name of the animation (ie: attack, idle...).
        - `sprites_paths`: list of paths to the sprites.
        - `period`: number of frame to wait between two sprites.
        """
        sprites = []
        for path in sprites_paths:
            sprite = pygame.image.load('sprites/'+path)
            sprites.append(sprite)
        self.animations[name] = Animation(name, sprites, period)

    def move(self, dest, speed):
        """
        Move the entity to a new location at a given speed.

        Arguments:
        - `dest`: a tuple (x, y) giving the destination's coordinates.
        - `speed`: movespeed in pixel per frame.
        """
        self.pos = list(dest)
        self.dest = [(dest[0] + 1)*SQUARE_SIZE - self.width, (dest[1] + 1)*SQUARE_SIZE - self.height]
        if dest[1] < self.pos[1]:
            play_anim('move_up')
        elif dest[0] > self.pos[0]:
            play_anim('move_right')
        elif dest[1] > self.pos[1]:
            play_anim('move_down')
        elif dest[0] < self.pos[0]:
            play_anim('move_left')

        self.speed = speed


    def update(self):
        """
        Give a timer's tick to the entity so it redraw itself and give an image to display to the world.

        Return: A pygame.Surface object.
        """
        if self.dest != self.cur_pos:
            print('movement start')
            vect = (self.dest[0] - self.cur_pos[0], self.dest[1] - self.cur_pos[1])
            norm = sqrt(vect[0]**2 + vect[1]**2)
            vect = (self.speed * vect[0] / norm, self.speed * vect[1] / norm)
            oldpos = self.cur_pos
            self.cur_pos = [self.cur_pos[0] + vect[0], self.cur_pos[1] + vect[1]]
            if (oldpos[0] < self.dest[0] < self.cur_pos[0]) or (oldpos[0] > self.dest[0] > self.cur_pos[0]):
                self.cur_pos[0] = self.dest[0]
                print('x updated')
            if (oldpos[1] < self.dest[1] < self.cur_pos[1]) or (oldpos[1] > self.dest[1] > self.cur_pos[1]):
                self.cur_pos[1] = self.dest[1]
                print('y updated')

        if self.animations[self.current_anim].end:
            self.play_anim(self.default_anim)
        return self.animations[self.current_anim].next_frame()


    def play_anim(self, name):
        """
        Change the animation being played if given animation exists.

        Arguments:
        - `name`: the name of the animation to be played.
        """
        if name in self.animations:
            self.current_anim = name
            self.animations[name].reset()



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
        - `frame_elapsed`: number of frame elapsed since the animation started.
        - `current_sprite`: the current displayed sprite.
        - `nb_sprites`: the number of sprites in the animation.
        - `end`: a boolean (True : ended, False : playing).
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

        Return: A pygame.Surface object.
        """
        self.frame_elapsed += 1
        if self.frame_elapsed >= self.period:
            self.frame_elapsed = 0
            if self.current_sprite < self.nb_sprites - 1:
                self.current_sprite += 1
            else:
                self.end = True
        return self.sprites[self.current_sprite]
