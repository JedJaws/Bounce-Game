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


"""A Ball class for the bouncing ball demo."""

import os.path
from random import randint
from math import isclose
import pygame
from game import rgbcolors


def random_velocity(min_val=1, max_val=3):
    """Generate a random velocity in a plane, return it as a Vector2"""
    random_x = randint(min_val, max_val)
    random_y = randint(min_val, max_val)
    if randint(0, 1):
        random_x *= -1
    if randint(0, 1):
        random_y *= -1
    return pygame.Vector2(random_x, random_y)


def random_color():
    """Return a random color."""
    return pygame.Color(randint(0, 255), randint(0, 255), randint(0, 255))


# This is the class we discussed in class. You can have this as a standalone
# definition of a circle's geometry or you can fold the Circle and Ball classes
# together into a single class definition. Your choice.
class Circle:
    """Class representing a circle with a bounding rect."""

    def __init__(self, center_x, center_y, radius):
        center_x = randint(25, 775)
        center_y = randint(25, 775)
        self._center = pygame.Vector2(center_x, center_y)
        self._radius = radius

    @property
    def radius(self):
        """Return the circle's radius"""
        return self._radius

    @property
    def center(self):
        """Return the circle's center."""
        return self._center

    @property
    def rect(self):
        """Return bounding Rect; calculate it and create a new Rect instance"""
        left = self._center[0] - self._radius
        top = self._center[1] - self._radius
        width = 2 * self._radius
        return pygame.Rect(left, top, self.width, self.height)

    @property
    def width(self):
        """Return the width of the bounding box the circle is in."""
        return self._radius * 2

    @property
    def height(self):
        """Return the height of the bounding box the circle is in."""
        return self._radius * 2

    def squared_distance_from(self, other_circle):
        """Squared distance from self to other circle."""
        return (other_circle.center - self._center).length_squared()

    def distance_from(self, other_circle):
        """Distance from self to other circle"""
        return (other_circle.center - self._center).length()

    def move_ip(self, x_cent, y_cent):
        """Move circle in place, update the circle's center"""
        self._center = self._center + pygame.Vector2(x_cent, y_cent)

    def move(self, x_cent, y_cent):
        """Move circle, return a new Circle instance"""
        center = self._center + pygame.Vector2(x_cent, y_cent)
        return Circle(center, self._radius)

    def stay_in_bounds(self, xmin, xmax, ymin, ymax):
        """Update the position of the circle so that it remains"""
        """ within the rectangle defined by xmin, xmax, ymin, ymax."""
        if (self._circle.center.x + self._circle.radius) >= xmax or (
            self._circle.center.x - self._circle.radius
        ) <= xmin:
            # print('Horizontal bounce')
            self._velocity.x = self._velocity.x * -1

        if (self._circle.center.y - self._circle.radius) <= ymin or (
            self._circle.center.y + self._circle.radius
        ) >= ymax:
            # print('Vertical bounce')
            self._velocity.y = self._velocity.y * -1


class Ball:
    """A class representing a moving ball."""

    default_radius = 25

    main_dir = os.path.split(os.path.abspath(__file__))[0]
    data_dir = os.path.join(main_dir, 'data')
    # Feel free to change the sounds to something else.
    # Make sure you have permssion to use the sound effect file and document
    # where you retrieved this file, who is the author, and the terms of
    # the license.
    bounce_sound = os.path.join(data_dir, 'Boing.aiff')
    reflect_sound = os.path.join(data_dir, 'Monkey.aiff')

    def __init__(self, name, center_x, center_y, sound_on=True):
        """Initialize a bouncing ball."""
        # The name can be any string. The best choice is an integer.
        self._name = name
        # Yes, we could define the details about our geometry in the Ball
        # class or we can define the geometry in an instance variable.
        # It is up to you if you want to separate them out or integrate them
        # together.
        self._circle = Circle(center_x, center_y, Ball.default_radius)
        self._color = random_color()
        self._velocity = random_velocity()
        self._sound_on = sound_on
        self._bounce_count = randint(5, 10)
        self._is_alive = True
        self._draw_text = False
        font = pygame.font.SysFont(None, Ball.default_radius)
        self._name_text = font.render(str(self._name), True, rgbcolors.black)
        try:
            self._bounce_sound = pygame.mixer.Sound(Ball.bounce_sound)
            self._bounce_channel = pygame.mixer.Channel(2)
        except pygame.error as pygame_error:
            print(f'Cannot open {Ball.bounce_sound}')
            raise SystemExit(1) from pygame_error
        try:
            self._reflect_sound = pygame.mixer.Sound(Ball.reflect_sound)
            self._reflect_channel = pygame.mixer.Channel(3)
        except pygame.error as pygame_error:
            print(f'Cannot open {Ball.reflect_sound}')
            raise SystemExit(1) from pygame_error

    def toggle_draw_text(self):
        """Toggle the debugging text where each circle's name is drawn."""
        self._draw_text = not self._draw_text

    def draw(self, surface):
        """Draw the circle to the surface."""
        pygame.draw.circle(surface, self.color, self.center, self.radius)
        if self._draw_text:
            surface.blit(
                self._name_text,
                self._name_text.get_rect(center=self._circle.center),
            )

    def wall_reflect(self, xmin, xmax, ymin, ymax):
        """Reflect the ball off of a wall,"""
        """play a sound if the sound flag is on."""
        if (self._circle.center.x + self._circle.radius) >= xmax or (
            self._circle.center.x - self._circle.radius
        ) <= xmin:
            # print('Horizontal bounce')
            self._velocity.x = self._velocity.x * -1

        if (self._circle.center.y - self._circle.radius) <= ymin or (
            self._circle.center.y + self._circle.radius
        ) >= ymax:
            # print('Vertical bounce')
            self._velocity.y = self._velocity.y * -1

    def bounce(self, other_ball):
        """Bounce the ball off of another ball,"""
        """ play a sound if the ball is no alive."""
        normal = other_ball.center - self.center
        self._velocity = self._velocity.reflect(normal)
        self._bounce_sound.play()

    def collide_with(self, other_ball):
        """Return true if self collides with other_ball."""
        return self._circle.distance_from(other_ball._circle) <= (
            self.radius + other_ball.radius
        )

    def separate_from(self, other_ball, rect):
        """Separate a ball from the other ball"""
        """ so they are no longer overlapping."""
        overlap_distance = (self.radius + other_ball.radius) - (
            self._circle.distance_from(other_ball._circle)
        )

        half_overlap_distance = overlap_distance / 2

        velocity = self._velocity * -1
        if not other_ball.is_alive:
            factor = 2
        else:
            factor = 1
        velocity = velocity * half_overlap_distance * factor
        self.circle.move_ip(*velocity)

        velocity = other_ball._velocity * -1
        if not self.is_alive:
            factor = 2
        else:
            factor = 1
        velocity = velocity * half_overlap_distance * factor
        other_ball.circle.move_ip(*velocity)

        # reverse_velocity = self._velocity * -1
        # self._circle.move_ip(*(reverse_velocity * half_overlap_distance))

        # reverse_velocity = other_ball._velocity * -1
        # other_ball._circle.move_ip(*\
        # (reverse_velocity * half_overlap_distance))

    @property
    def name(self):
        """Return the ball's name."""
        return self._name

    @property
    def rect(self):
        """Return the ball's rect."""
        return self._circle.rect

    @property
    def circle(self):
        """Return the ball's circle."""
        return self._circle

    @property
    def center(self):
        """Return the ball's center."""
        return self._circle.center

    @property
    def radius(self):
        """Return the ball's radius"""
        return self._circle.radius

    @property
    def color(self):
        """Return the color of the ball."""
        return self._color

    @property
    def velocity(self):
        pass

    @property
    def is_alive(self):
        """Return true if the ball is still alive."""
        # TODO
        self._bounce_count = self._bounce_count - 1

        if self._bounce_count == 0:
            self.stop()
            self._color = rgbcolors.white
            return not self._is_alive

        if self._bounce_count > 0:
            return self._is_alive

    def toggle_sound(self):
        """Turn off the sound effects."""
        # TODO
        self._sound_on = not self._sound_on

    def too_close(self, x_point, y_point, min_dist):
        """Is the ball too close to some point by some min_dist?"""
        # TODO
        point = pygame.Vector2(x_point, y_point)
        distance = (self.center - point).length()
        return distance <= min_dist

    def stop(self):
        """Stop the ball from moving."""
        # TODO
        self._velocity = pygame.Vector2(0, 0)

    def set_velocity(self, x_vel, y_vel):
        """Set the ball's velocity."""
        # TODO
        self._velocity = pygame.Vector2(x_vel, y_vel)

    def update(self):
        """Update the ball's position"""
        # TODO
        self._circle.move_ip(*self._velocity)

    def __str__(self):
        """Ball stringify."""
        # return f'Ball'({self._name}, {self._circle.center}, {self._color})
