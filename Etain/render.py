#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import pygame
from pygame.locals import *
import pickle
sys.path.append("../shared/")
from area import Area
import entity
import ui

SQUARE_SIZE = 32


class Render():
    """
    Render engine.

    Display entities, map and catch mouse and keyboard input to transfer them to the event handler.
    """

    def __init__(self, height, width, title, fps, send_queue, receive_queue):
        """
        Initialize the window's display.

        Attributes:
        - `font`: the font to use for texts.
        - `fps`: set the frame rate (caution : increasing the frame rate increase the game's speed).
        - `fps_render`: a boolean telling render to display fps or not.
        - `grid_render`: a boolean telling render to display the grid or not.
        - `height`: the height of the window (given in square, size in pixel of each square given by SQUARE_SIZE).
        - `width`: the width of the window (given in square).
        - `l_entities`: list of entities currently on the map.
        - `UI`: the UI handler.
        - `s_queue`: the queue used to send commands to Dana.
        - `r_queue`: the queue used to receive commands from Dana.
        - `me`: uid of the entity controlled by the player.
        - `clock`: A pygame timer.
        - `title`: set the caption in windowed mode.
        """
        pygame.init()
        self.font = pygame.font.SysFont(None, 24)
        self.fps = fps
        self.fps_render = False
        self.grid_render = False
        self.height = height
        self.width = width
        self.l_entities = entity.List()
        self.UI = ui.UI(self)
        self.s_queue = send_queue
        self.r_queue = receive_queue
        self.me = None
        self.clock = pygame.time.Clock()

        self.window = pygame.display.set_mode((width*SQUARE_SIZE, height*SQUARE_SIZE), 0)
        pygame.display.set_caption(title)
        self.s_queue.put('GET_ENTITIES')


    def run(self):
        """
        Main programm's loop (process, display and inputs).
        """

        while(True):
            self.UI.run()
            self.draw_world()
            self.draw_entities()
            self.draw_overlay()

            pygame.display.flip()
            self.clock.tick(self.fps)


    def draw_overlay(self):
        """
        """
        if self.fps_render:
            # fps displaying
            text = self.font.render(str(self.clock.get_fps()), False, (0, 0, 0))
            text_Rect = text.get_rect()
            text_Rect.right = self.width*SQUARE_SIZE - 10
            text_Rect.top = 10
            self.window.blit(text, text_Rect)
        # battle state displaying
        text = self.font.render(self.UI.round_state, False, (0, 0, 0))
        text_Rect = text.get_rect()
        text_Rect.left = 10
        text_Rect.top = 10
        self.window.blit(text, text_Rect)


    def draw_world(self):
        """
        Display the ground's tiles'.
        """
        for j in xrange(0, self.height):
            top = j * SQUARE_SIZE
            for i in xrange(0, self.width):
                left = i * SQUARE_SIZE
                self.window.blit(self.area.tiles[self.area[j][i]], (left, top))
        if self.grid_render:
            for i in xrange(1, self.width):
                pygame.draw.line(self.window, (50, 50, 50), (i*SQUARE_SIZE, 0), (i*SQUARE_SIZE, self.height*SQUARE_SIZE))
            for i in xrange(1, self.height):
                pygame.draw.line(self.window, (50, 50, 50), (0, i*SQUARE_SIZE), (self.width*SQUARE_SIZE, i*SQUARE_SIZE))


    def register_entity(self, pos, width, height, hp, uid, anim_path):
        """
        Register a New graphic entity to the world.

        Arguments:
        - `pos`: a tuple (x, y) giving the coordinates where to spawn the entity.
        - `width`: the width of the entity (used for display only).
        - `height`: the height of the entity (used for display only).
        - `hp`: current and max hp of the entity.
        - `uid`: the unique id of the entity (int).
        - `anim_path`: the anim file of the entity.
        """
        self.l_entities.add_entity(pos, width, height, hp, uid, anim_path)


    def remove_entity(self, uid):
        """
        Remove a graphical entity from the world.
        """
        del self.l_entities[uid]


    def draw_entities(self):
        """
        Draw every entities on the map in their current state of animation.
        """
        for i in xrange(self.height):
            layer = self.l_entities.get_layer(i)
            for entity in layer.values():
                image = entity.update()
                ellipse_Rect = (entity.pixel_pos[0], entity.pixel_pos[1] + entity.height - 3 * SQUARE_SIZE / 4, SQUARE_SIZE, 3 * SQUARE_SIZE / 4)

                # entity and circle
                pygame.draw.ellipse(self.window, entity.faction_color, ellipse_Rect , 2)
                self.window.blit(image, entity.pixel_pos)

                # health bar
                self.window.fill((0, 0, 0, 200), (entity.pixel_pos[0] + 2, entity.pixel_pos[1] - 10,
                                                  SQUARE_SIZE - 4, 6))
                hp_ratio = entity.hp/float(entity.max_hp)
                self.window.fill((0, 200, 0), (entity.pixel_pos[0] + 2, entity.pixel_pos[1] - 10,
                                               round(hp_ratio*(SQUARE_SIZE - 4)), 6))
                pygame.draw.rect(self.window, entity.faction_color, (entity.pixel_pos[0] + 1, entity.pixel_pos[1] - 11,
                                                                     SQUARE_SIZE - 2, 8), 1)


    def load_map(self, path):
        """
        Load the map and entities' informations from a file.

        Arguments:
        - `path`: the path to the save file of the map to load.
        """
        f_map = open(path, 'r')
        self.area = pickle.load(f_map)
        self.area.load_tiles()
        f_map.close()


    def play_music(self, path):
        """
        Load and play background music.

        Arguments:
        - `path`: path to the music file (ogg, wav, midi).
        """
        pygame.mixer.music.load(path)
        pygame.mixer.music.play(-1)


    def stop_music(self):
        """
        Stop the background music.
        """
        pygame.mixer.music.stop()


    def __del__(self):
        """
        Unload the display and exit the programm.
        """
        pygame.quit()
