#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
try:
    import pygame
    from pygame.locals import *
except ImportError:
    print "Veuillez installer la bibliothèque pygame : http://www.pygame.org/"
    sys.exit()
import pickle
sys.path.append("../shared/")
from area import Area
import entity
import ui
import particle
from locales import *
from math import sqrt


class Render():
    """
    Render engine.

    Display entities, map and catch mouse and keyboard input to transfer them to the event handler.
    """

    def __init__(self, send_queue, receive_queue, path, pseudo):
        """
        Initialize the window's display.

        Attributes:
        - `font`: the font to use for texts.
        - `menu_font`: the font to use for menus.
        - `banner_font`: the font to use for banners.
        - `speech_font`: the font to use for speech bubbles.
        - `chat_font`: the font to use for chat.
        - `particles`: list of current particles.
        - `rdy`: set if the player is ready to play.
        - `fps_render`: a boolean telling render to display fps or not.
        - `grid_render`: a boolean telling render to display the grid or not.
        - `menu`: a boolean telling render to display the menu or not.
        - `chat`: a list [True|False, text, int], text is the text being written.
        - `banner_fight`: True if render display the banner "Fight start".
        - `banner_next`: True if render should display "Next Round" banner.
        - `l_entities`: list of entities currently on the map.
        - `UI`: the UI handler.
        - `s_queue`: the queue used to send commands to Dana.
        - `r_queue`: the queue used to receive commands from Dana.
        - `me`: uid of the entity controlled by the player.
        - `path`: The path the player wants to move on.
        - `target`: The target the player wants to attack.
        - `clock`: A pygame timer.
        - `bubbles`: A dictionnary of all bubbles currently displaying.
        - `Surfaces`: A dictionnary of pygame.Surface.
        - `cursor`: current cursor used.
        """
        pygame.init()

        # Fonts
        self.font = pygame.font.SysFont(None, 24)
        self.button_font = pygame.font.SysFont(None, 48)
        self.button_font.set_bold(True)
        self.menu_font = pygame.font.SysFont(None, 16)
        self.banner_font = pygame.font.SysFont(None, 128)
        self.speech_font = pygame.font.SysFont("Monospace", 12)
        self.speech_font.set_bold(True)
        self.chat_font = pygame.font.SysFont(None, 16)

        self.particles = []
        self.end_frame = 0
        self.rdy = False
        self.fps_render = False
        self.grid_render = True
        self.menu = False
        self.chat = [False, '', 0]
        self.banner_fight = False
        self.banner_next = False
        self.l_entities = entity.List()
        self.UI = ui.UI(self)
        self.s_queue = send_queue
        self.r_queue = receive_queue
        self.me = None
        self.path = None
        self.target = None
        self.clock = pygame.time.Clock()
        self.bubbles = {}
        self.start_choice = 0

        # Surfaces and graphics loading
        self.Surface = {'map' : pygame.Surface((WIDTH, HEIGHT), HWSURFACE),
                        'grid' : pygame.Surface((WIDTH, HEIGHT), HWSURFACE | SRCALPHA),
                        'menu' : pygame.Surface((MENU_WIDTH, MENU_HEIGHT), HWSURFACE),
                        'chat' : pygame.Surface((CHAT_WIDTH, CHAT_HEIGHT), HWSURFACE | SRCALPHA),
                        'end' : pygame.Surface((WIDTH, HEIGHT), HWSURFACE | SRCALPHA),
                        'health' : {ALLY : pygame.Surface((H_WIDTH, H_HEIGHT), HWSURFACE | SRCALPHA),
                                    ENNEMY : pygame.Surface((H_WIDTH, H_HEIGHT), HWSURFACE | SRCALPHA)}}

        # Set display
        self.window = pygame.display.set_mode((WIDTH, HEIGHT), FULLSCREEN | HWSURFACE | DOUBLEBUF)
        pygame.display.set_caption(TITLE)
        self.cursor = "arrow"
        self.use_cursor(ARROW)
        self.preload(path)

        self.s_queue.put('SET:pseudo:'+pseudo.replace(':', ' '))
        self.s_queue.put('GET_ENTITIES')
        self.play_music("sounds/battle.ogg")


    def run(self):
        """
        Main programm's loop (process, display and inputs).
        """
        gear = pygame.image.load("sprites/gear.png")
        fight = pygame.image.load("sprites/fight.png")
        while(True):
            self.UI.run()

            self.window.blit(self.Surface['map'], (0, 0))
            if self.grid_render:
                self.window.blit(self.Surface['grid'], (0, 0))
            if self.path is not None:
                for pos in self.path:
                    square = (pos[0] * SQUARE_SIZE, pos[1] * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
                    self.window.fill(BLUE, square)

            self.draw_entities()
            self.draw_particles()
            self.draw_overlay()

            if self.target is not None:
                square_pos = (self.target.pixel_pos[0] + (self.target.width - SQUARE_SIZE) / 2, self.target.pixel_pos[1] - SQUARE_SIZE - 8)
                self.window.blit(fight, square_pos)

            self.window.blit(gear, (WIDTH - 18, 2))

            pygame.display.flip()
            self.clock.tick(FPS)


    def get_uid(self, entity):
        """
        """
        result = None
        for uid in self.l_entities:
            if self.l_entities[uid] == entity:
                result = uid
                break
        return result


    def draw_particles(self):
        """
        """
        for particle in self.particles:
            self.window.blit(particle.update(), particle.pos)

        for i in xrange(len(self.particles)):
            if self.particles[i].dead:
                del self.particles[i]
                break


    def draw_overlay(self):
        """
        """
        # fps displaying
        if self.fps_render:
            self.text("%1.1f" % self.clock.get_fps(), top = 2, right = WIDTH - 18)

        # battle state displaying
        self.text(self.UI.round_state, left = 35, top = 10)

        if self.banner_fight:
            self.window.fill(BEIGE, (0, 200, WIDTH, HEIGHT - 400))
            self.text("FIGHT !", font=self.banner_font, centerx=WIDTH / 2, centery=HEIGHT / 2, color=RED)

        if self.banner_next:
            self.window.fill(BEIGE, (0, 200, WIDTH, HEIGHT - 400))
            self.text("NEXT ROUND !", font=self.banner_font, centerx=WIDTH / 2, centery=HEIGHT / 2, color=RED)

        # Speech bubbles
        del_uid = None
        for uid in self.bubbles:
            bubble = self.bubbles[uid]
            ent = self.l_entities[bubble[0]]
            pos = (ent.pixel_pos[0] + ent.width, ent.pixel_pos[1])
            pygame.draw.polygon(self.window, WHITE, ((pos[0] - 5, pos[1] + 10), (pos[0] + 40, pos[1] - 20), (pos[0] + 15, pos[1] - 20)))
            pygame.draw.ellipse(self.window, WHITE, (pos[0] - 10, pos[1] - 50, 100, 50))
            self.text(bubble[1], self.speech_font, top=pos[1] - 35, left=pos[0] + 5, alias=False)
            bubble[2] -= 1
            if bubble[2] <= 0:
                del_uid = uid
        if del_uid is not None:
            del self.bubbles[del_uid]

        # Actions buttons
        if self.UI.round_state == 'CHOICE' and not self.UI.confirm and self.l_entities[self.me].alive:
            self.window.fill(GREEN, (20, HEIGHT - 70, 90, 20))
            self.text('Confirmer', top=HEIGHT - 67, left=25)
            self.window.fill(RED, (20, HEIGHT - 40, 90, 20))
            self.text('Annuler', top=HEIGHT - 37, left=32)

        # Menu display
        if self.menu:
            menu_x = (WIDTH - MENU_WIDTH) / 2
            menu_y = (HEIGHT - MENU_HEIGHT) / 2
            self.window.blit(self.Surface['menu'], (menu_x, menu_y))
            if self.grid_render:
                self.window.fill(BLACK, (menu_x + 32, menu_y + 52, 6, 6))
            if self.fps_render:
                self.window.fill(BLACK, (menu_x + 32, menu_y + 92, 6, 6))

        # Chat display
        if self.chat[0]:
            self.window.blit(self.Surface['chat'], (4, HEIGHT - CHAT_HEIGHT - 4))
            history_y = HEIGHT - CHAT_HEIGHT
            for text in self.UI.chat_history:
                self.text(text, font=self.chat_font, top=history_y, left=8, color=WHITE)
                history_y += 15
            self.chat[2] += 1
            if self.chat[2] >= FPS / 2:
                self.text(self.chat[1] + '|', font=self.chat_font, top=HEIGHT - 17, left=8)
                if self.chat[2] >= FPS:
                    self.chat[2] = 0
            else:
                self.text(self.chat[1], font=self.chat_font, top=HEIGHT - 17, left=8)

        # Ready to play button
        if self.UI.round_state == 'PLAYERS_CONNECTION':
            if not self.rdy:
                self.window.fill(GREY, ((WIDTH - 200)/2, (HEIGHT - 50)/2, 200, 50))
            else:
                self.window.fill(DARKGREEN, ((WIDTH - 200)/2, (HEIGHT - 50)/2, 200, 50))
            self.text('READY !', font=self.button_font, centerx=WIDTH/2, centery=HEIGHT/2, color=WHITE)

        # Timer choice display
        if self.UI.round_state == 'CHOICE':
            pygame.draw.circle(self.window, GREY, (15, 15), 10)
            time_left = max(0, TIME_CHOICE + self.start_choice - pygame.time.get_ticks())
            angle = ((time_left / TIME_CHOICE) * 3 + 1) * PI / 2
            diag = sqrt(2) * 5
            pointlist = [(15, 15), (15, 5)]
            s_angle = 0.5
            if angle > PI / 2:
                s_angle = 0.75
                pointlist.append((15 - diag, 15 - diag))
            if angle > PI * 0.75:
                s_angle = 1
                pointlist.append(( 5, 15))
            if angle > PI:
                s_angle = 1.25
                pointlist.append((15 - diag, 15 + diag))
            if angle > PI * 1.25:
                s_angle = 1.5
                pointlist.append((15, 25))
            if angle > PI * 1.5:
                s_angle = 1.75
                pointlist.append((15 + diag, 15 + diag))
            if angle > PI * 1.75:
                s_angle = 2
                pointlist.append((25, 15))
            if angle > PI * 2:
                s_angle = 2.25
                pointlist.append((15 + diag, 15))
            if angle > PI * 2.5:
                s_angle = 2.5
                pointlist.append((15, 5))
            pointlist.append((15, 15))
            pygame.draw.polygon(self.window, WHITE, tuple(pointlist))
            pygame.draw.arc(self.window, WHITE, (5, 5, 20, 20), PI / 2, s_angle * PI, 2)
            if time_left < 3000 :
                pygame.draw.circle(self.window, RED, (15, 15), 12, 2)
            else:
                pygame.draw.circle(self.window, GREEN, (15, 15), 12, 2)

        # Win/Lose screens
        if self.UI.round_state == 'WIN':
            self.end_frame = min(255, self.end_frame + 1)
            self.Surface['end'].fill((255, 255, 255, self.end_frame), (0, 0, WIDTH, HEIGHT))
            self.text("YOU WIN !", surf=self.Surface['end'], font=self.banner_font, centerx=WIDTH / 2,
                      centery=HEIGHT / 2, color=YELLOW)
            self.window.blit(self.Surface['end'], (0, 0))
        elif self.UI.round_state == 'LOSE':
            self.end_frame = min(255, self.end_frame + 1)
            self.Surface['end'].fill((180, 0, 0, self.end_frame), (0, 0, WIDTH, HEIGHT))
            self.text("YOU LOSE !", surf=self.Surface['end'], font=self.banner_font, centerx=WIDTH / 2,
                      centery=HEIGHT / 2, color=BLACK)
            self.window.blit(self.Surface['end'], (0, 0))


    def effect(self, type, id=None, target_id=None, params=None):
        """
        """
        if type.lower() == 'dmg':
            entity = self.l_entities[target_id]
            entity.hp -= int(params[0])
            pos = (entity.pixel_pos[0] + entity.width / 2, entity.pixel_pos[1] + 20)
            self.particles.append(particle.Particle('dmg', params, FPS * 2, pos))
        elif type.lower() == 'dead':
            self.l_entities[target_id].die()
        else:
            entity = self.l_entities[target_id]
            pos = (entity.pixel_pos[0] + entity.width / 2, entity.pixel_pos[1] + entity.height / 2)
            self.particles.append(particle.Particle(type, params, 100, pos))


    def text(self, msg, font=None, top=None, right=None, left=None, bottom=None, centerx=None, centery=None,
             color=(0, 0, 0), alias=True, surf=None):
        """
        """
        if font is None:
            font = self.font
        if surf is None:
            surf = self.window
        text = font.render(msg, alias, color)
        text_Rect = text.get_rect()

        if top is not None:
            text_Rect.top = top
        elif bottom is not None:
            text_Rect.bottom = bottom
        else:
            text_Rect.centerx = centerx
        if right is not None:
            text_Rect.right = right
        elif left is not None:
            text_Rect.left = left
        else:
            text_Rect.centery = centery

        self.font = pygame.font.SysFont(None, 24)
        surf.blit(text, text_Rect)


    def draw_entities(self):
        """
        Draw every entities on the map in their current state of animation.
        """
        for i in xrange(HEIGHT):
            layer = self.l_entities.get_layer(i)
            for entity in layer.values():
                image = entity.update()
                self.draw_entity_HUD(entity.faction, entity.hp, entity.max_hp, entity.pixel_pos, entity.height, entity.width)
                self.window.blit(image, entity.pixel_pos)


    def end_anims(self):
        """
        """
        result = True
        for entity in self.l_entities.values():
            if entity.is_still_animated():
                result = False
                break
        return result


    def draw_entity_HUD(self, faction, hp, max_hp, pos, height, width):
        """
        """
        if faction != NEUTRE:
            # select circle
            ellipse_Rect = (pos[0] + (width - SQUARE_SIZE)/ 2, pos[1] + height - 3 * SQUARE_SIZE / 4, SQUARE_SIZE, 3 * SQUARE_SIZE / 4)
            pygame.draw.ellipse(self.window, FACTION_COLOR[faction], ellipse_Rect , 2)

            # health bar
            self.window.blit(self.Surface['health'][faction], (pos[0] + (width - SQUARE_SIZE)/2, pos[1] - 10))
            hp_ratio = hp/float(max_hp)
            self.window.fill(GREEN, (pos[0] + (width - SQUARE_SIZE) / 2 + 1, pos[1] - 9, round(hp_ratio*(H_WIDTH - 2)), H_HEIGHT - 2))


    def preload(self, map_path):
        """
        Preload graphics from the files.

        Arguments:
        - `path`: the path to the save file of the map to load.
        """
        f_map = open(map_path, 'r')
        area = pickle.load(f_map)
        area.load_tiles()
        f_map.close()
        for j in xrange(0, ROWS):
            top = j * SQUARE_SIZE
            for i in xrange(0, COLUMNS):
                left = i * SQUARE_SIZE
                self.Surface['map'].blit(area.tiles[area[j][i]], (left, top))

        # Create the grid
        for i in xrange(1, COLUMNS):
            pygame.draw.line(self.Surface['grid'], (50, 50, 50), (i * SQUARE_SIZE, 0), (i * SQUARE_SIZE, HEIGHT))
        for i in xrange(1, ROWS):
            pygame.draw.line(self.Surface['grid'], (50, 50, 50), (0, i * SQUARE_SIZE), (WIDTH, i * SQUARE_SIZE))

        # Create the menu
        self.Surface['menu'].fill(GREY)
        self.Surface['menu'].fill(WHITE, (30, 50, 10, 10))
        self.Surface['menu'].fill(WHITE, (30, 90, 10, 10))
        self.text("Afficher la grille.", self.menu_font, top=50, left=50, surf=self.Surface['menu'])
        self.text("Afficher les IPS.", self.menu_font, top=90, left=50, surf=self.Surface['menu'])
        pygame.draw.polygon(self.Surface['menu'], RED, ((MENU_WIDTH - 12, 9), (MENU_WIDTH - 16, 5), (MENU_WIDTH - 14, 3),
                                                        (MENU_WIDTH - 10, 7), (MENU_WIDTH - 6, 3), (MENU_WIDTH - 4, 5),
                                                        (MENU_WIDTH - 8, 9), (MENU_WIDTH - 4, 13), (MENU_WIDTH - 6, 15),
                                                        (MENU_WIDTH - 10, 11), (MENU_WIDTH - 14, 15), (MENU_WIDTH - 16, 13)))

        # Create Chat window
        self.Surface['chat'].fill(WHITE, (0, CHAT_HEIGHT - 15, CHAT_WIDTH, 15))
        self.fill_gradient(self.Surface['chat'], (0, 0, 0, 50), (0, 0, 0, 255), (0, 0, CHAT_WIDTH, 200))

        # Create Health bars
        for faction in self.Surface['health']:
            self.Surface['health'][faction].fill((0, 0, 0, 200))
            pygame.draw.rect(self.Surface['health'][faction], FACTION_COLOR[faction], (0, 0, H_WIDTH, H_HEIGHT), 1)


    def use_cursor(self, name):
        """
        """
        self.cursor, cursor = name
        hotspot = None
        for y in range(len(cursor)):
            for x in range(len(cursor[y])):
                if cursor[y][x] in ['x', ',', 'O']:
                    hotspot = x,y
                    break
            if hotspot != None:
                break
        if hotspot == None:
            raise Exception("No hotspot specified for cursor !")
        s = []
        for line in cursor:
            s.append(line.replace('x', 'X').replace(',', '.').replace('O', 'o'))
        curs, mask = pygame.cursors.compile(s)
        size = len(cursor[0]), len(cursor)
        pygame.mouse.set_cursor(size, hotspot, curs, mask)


    def fill_gradient(self, surface, color, gradient, rect=None, vertical=True):
        """
        fill a surface with a gradient pattern

        Arguments:
        - `color`: starting color.
        - `gradient`: final color.
        - `rect`: the rect to fill.
        - `'vertical`: True=vertical, False=horizontal.
        """
        if rect is None:
            rect = surface.get_rect()
            x1, x2 = rect.left, rect.right
            y1, y2 = rect.top, rect.bottom
        else:
            x1, y1, x2, y2 = rect[0], rect[1], rect[0] + rect[2], rect[1] + rect[3]
        if vertical:
            h = y2 - y1
        else:
            h = x2 - x1
        if len(color) == 3:
            rate = (float(gradient[0] - color[0])/h, float(gradient[1] - color[1])/h, float(gradient[2] - color[2])/h)
            if vertical:
                for line in range(y1, y2):
                    color = (color[0] + rate[0], color[1] + rate[1], color[2] + rate[2])
                    pygame.draw.line(surface, color, (x1, line), (x2, line))
            else:
                for col in range(x1, x2):
                    color = (color[0] + rate[0], color[1] + rate[1], color[2] + rate[2])
                    pygame.draw.line(surface, color, (col, y1), (col, y2))
        elif len(color) == 4:
            rate = (float(gradient[0] - color[0])/h, float(gradient[1] - color[1])/h, float(gradient[2] - color[2])/h,
                    float(gradient[3] - color[3])/h)
            if vertical:
                for line in range(y1, y2):
                    color = (color[0] + rate[0], color[1] + rate[1], color[2] + rate[2], color[3] + rate[3])
                    pygame.draw.line(surface, color, (x1, line), (x2 , line))
            else:
                for col in range(x1, x2):
                    color = (color[0] + rate[0], color[1] + rate[1], color[2] + rate[2], colot[3] + rate[3])
                    pygame.draw.line(surface, color, (x1, line), (x2 , line))


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
