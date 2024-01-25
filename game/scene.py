# Christian Verry
# CPSC 386-03
# 2022-03-07
# CJVerry@csu.fullerton.edu
# @JedJaws
#
# Lab 05-00
#
# This module is my first visual game
#


"""Scene objects for making games with PyGame."""

from random import randint, randrange
import pygame
from more_itertools import grouper
from game import rgbcolors
from game.ball import Ball
from game.animation import Explosion


class Scene:
    """Base class for making PyGame Scenes."""

    def __init__(self, screen, background_color, soundtrack=None):
        """Scene initializer"""
        self._screen = screen
        self._background = pygame.Surface(self._screen.get_size())
        self._background.fill(background_color)
        self._frame_rate = 60
        self._is_valid = True
        self._soundtrack = soundtrack
        self._render_updates = None

    def draw(self):
        """Draw the scene."""
        self._screen.blit(self._background, (0, 0))

    def process_event(self, event):
        """Process a game event by the scene."""
        # This should be commented out or removed
        # since it generates a lot of noise.
        # print(str(event))
        if event.type == pygame.QUIT:
            print('Good Bye!')
            self._is_valid = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            print('Bye bye!')
            self._is_valid = False

    def is_valid(self):
        """Is the scene valid? A valid scene can be used to play a scene."""
        return self._is_valid

    def render_updates(self):
        """Render all sprite updates."""
        pass

    def update_scene(self):
        """Update the scene state."""
        pass

    def start_scene(self):
        """Start the scene."""
        if self._soundtrack:
            try:
                pygame.mixer.music.load(self._soundtrack)
                pygame.mixer.music.set_volume(0.1)
            except pygame.error as pygame_error:
                print('Cannot open the mixer?')
                raise SystemExit('broken!!') from pygame_error
            pygame.mixer.music.play(-1)

    def end_scene(self):
        """End the scene."""
        if self._soundtrack and pygame.mixer.music.get_busy():
            pygame.mixer.music.fadeout(500)
            pygame.mixer.music.stop()

    def frame_rate(self):
        """Return the frame rate the scene desires."""
        return self._frame_rate


class EmptyPressAnyKeyScene(Scene):
    """Empty scene where it will invalidate when a key is pressed."""

    # def __init__(self, screen, background_color, soundtrack=None):
    #     super().__init__(screen, background_color, soundtrack)

    # def draw(self):
    #     """Draw the scene."""
    #     super().draw()

    def process_event(self, event):
        """Process game events."""
        super().process_event(event)
        if event.type == pygame.KEYDOWN:
            self._is_valid = False


class SplashScene(EmptyPressAnyKeyScene):
    """A splash screen with a message."""

    def __init__(self, screen, message, soundtrack=None):
        """Init the splash screen."""
        super().__init__(screen, rgbcolors.snow, soundtrack)
        self._message = message
        self._words_per_line = 5

    def _split_message(self):
        """Given a message, split it up according"""
        """ to how many words per line."""
        lines = [
            ' '.join(x).rstrip()
            for x in grouper(self._message.split(), self._words_per_line, '')
        ]
        for line in lines:
            yield line

    def draw(self):
        super().draw()
        (wid_scr, hei_scr) = self._screen.get_size()
        press_any_key_font = pygame.font.Font(
            pygame.font.get_default_font(), 18
        )
        press_any_key = press_any_key_font.render(
            'Press any key.', True, rgbcolors.black
        )
        press_any_key_pos = press_any_key.get_rect(
            center=(wid_scr / 2, hei_scr - 50)
        )

        font = pygame.font.Font(pygame.font.get_default_font(), 25)
        start_pos = (hei_scr / 2) - (
            (len(self._message.split()) // self._words_per_line) * 30
        )
        offset = 0
        for line in self._split_message():
            line = font.render(line, True, rgbcolors.black)
            line_pos = line.get_rect(center=(wid_scr / 2, start_pos + offset))
            offset += 30
            self._screen.blit(line, line_pos)
        self._screen.blit(press_any_key, press_any_key_pos)


class BlinkingTitle(EmptyPressAnyKeyScene):
    """A scene with blinking text."""

    def __init__(
        self, screen, message, color, size, background_color, soundtrack=None
    ):
        super().__init__(screen, background_color, soundtrack)
        self._message_color = color
        self._message_complement_color = (
            255 - color[0],
            255 - color[1],
            255 - color[2],
        )
        self._size = size
        self._message = message
        self._t = 0.0
        self._delta_t = 0.01

    def _interpolate(self):
        # This can be done with pygame.Color.lerp
        self._t += self._delta_t
        if self._t > 1.0 or self._t < 0.0:
            self._delta_t *= -1
        ball_color = rgbcolors.sum_color(
            rgbcolors.mult_color(
                (1.0 - self._t), self._message_complement_color
            ),
            rgbcolors.mult_color(self._t, self._message_color),
        )
        return ball_color

    def draw(self):
        super().draw()
        presskey_font = pygame.font.Font(
            pygame.font.get_default_font(), self._size
        )
        presskey = presskey_font.render(
            self._message, True, self._interpolate()
        )
        (wid_scr, hei_scr) = self._screen.get_size()
        presskey_pos = presskey.get_rect(center=(wid_scr / 2, hei_scr / 2))
        press_any_key_font = pygame.font.Font(
            pygame.font.get_default_font(), 18
        )
        press_any_key = press_any_key_font.render(
            'Press any key.', True, rgbcolors.black
        )
        (wid_scr, hei_scr) = self._screen.get_size()
        press_any_key_pos = press_any_key.get_rect(
            center=(wid_scr / 2, hei_scr - 50)
        )
        self._screen.blit(presskey, presskey_pos)
        self._screen.blit(press_any_key, press_any_key_pos)


class BouncingBallsScene(Scene):
    """Bounding balls demo."""

    def __init__(
        self, num_balls, screen, background_color, frame_rate, soundtrack=None
    ):
        super().__init__(screen, background_color, soundtrack)
        self._pause_game = False
        self._boundary_rect = self._screen.get_rect()
        self._balls = []

    def start_scene(self):
        super().start_scene()
        self._render_updates = pygame.sprite.RenderUpdates()
        Explosion.containers = self._render_updates

        (width, height) = self._screen.get_size()
        x_min = 0 + (Ball.default_radius * 2)
        x_max = width - (Ball.default_radius * 2)
        y_min = 0 + (Ball.default_radius * 2)
        y_max = height - (Ball.default_radius * 2)
        ball_count = randint(3, 50)

        for i in range(ball_count):
            point_too_close = True
            while point_too_close:
                x_coord = randint(x_min, x_max)
                y_coord = randint(y_min, y_max)
                point_too_close = False
                for ball in self._balls:
                    point_too_close = point_too_close or ball.too_close(
                        x_coord, y_coord, Ball.default_radius * 2.5
                    )

            self._balls.append(Ball(str(i), x_coord, y_coord, sound_on=False))
        # for ball in self._balls:
        #    ball.stop()

        self._balls[0]._circle._center = pygame.Vector2(
            randint(50, 750), randint(50, 750)
        )
        self._balls[0].set_velocity(11, 6)
        self._balls[0]._color = rgbcolors.red
        self._balls[0]._bounce_count = float('inf')

        # self._balls[1]._circle._center = pygame.Vector2(200, 400)
        # self._balls[1].set_velocity(0, 0)
        # self._balls[1]._color = rgbcolors.purple
        # self._balls[1]._bounce_count

        # self._balls[2]._circle._center = pygame.Vector2(10, 5)
        # self._balls[2].set_velocity(4, -2)
        # self._balls[2]._color = rgbcolors.blue
        # self._balls[2]._bounce_count

    def end_scene(self):
        super().end_scene()

    def _draw_boundaries(self):
        (w, h) = self._screen.get_size()
        pygame.draw.rect(
            self._screen,
            rgbcolors.yellow,
            self._boundary_rect,
            (w // 100),
            (w // 200),
        )

    def process_event(self, event):
        super().process_event(event)

        if event.type == pygame.KEYDOWN and event.key == pygame.K_a:
            for ball in self._balls:
                ball.toggle_draw_text()

        if event.type == pygame.KEYDOWN and event.key == pygame.K_s:
            for ball in self._balls:
                ball.toggle_sound()

        if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
            self._pause_game = not self._pause_game

        if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
            print('Explode')

        if event.type == pygame.KEYDOWN and event.key == pygame.K_x:
            self._is_valid = False

        if event.type == pygame.KEYDOWN and event.key == pygame.K_t:
            if self._soundtrack and pygame.mixer.music.get_busy():
                pygame.mixer.music.fadeout(500)
                pygame.mixer.music.stop()
            else:
                if self._soundtrack:
                    try:
                        pygame.mixer.music.load(self._soundtrack)
                    except pygame.error as pygame_error:
                        print('Cannot open the mixer?')
                        raise SystemExit('broken!!') from pygame_error
                    pygame.mixer.music.play(-1)

    def render_updates(self):
        if self._render_updates:
            self._render_updates.clear(self._screen, self._background)
            self._render_updates.update()
            dirty = self._render_updates.draw(self._screen)

    def draw(self):
        super().draw()
        for ball in self._balls:
            ball.draw(self._screen)
        self._draw_boundaries()

    def update_scene(self):
        if not self._pause_game:
            super().update_scene()
            for ball in self._balls:
                ball.update()
            for ball in self._balls:
                ball.wall_reflect(0, 800, 0, 800)
            for index, ball in enumerate(self._balls):
                for other_ball in self._balls[index + 1 :]:
                    if ball.collide_with(other_ball):
                        ball.is_alive
                        ball._bounce_sound.play()
                        if not ball.is_alive:
                            Explosion(ball)
                        if not other_ball.is_alive:
                            Explosion(other_ball)
                        ball.separate_from(other_ball, self._boundary_rect)
                        ball.bounce(other_ball)
                        other_ball.bounce(ball)

        # print('\n'.join(map(str, self._balls)))
