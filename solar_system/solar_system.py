import sys
import math
import datetime
from OpenGL.GL import *
from OpenGL.GLU import *
import pygame
from pygame.locals import *
from skyfield.api import load


class InnerSolarSystem(object):
    """ Main class for creating solar system
     Args:
        width (int): the width of the screen
        height (int): the height of the screen
    """
    def __init__(self,width=800,height=600):
        self.title = 'Inner Solar System'
        self.fps = 60
        self.width = width
        self.height = height
        self.planets = load('de421.bsp')
        self.date = datetime.datetime(1980, 1, 1)

        self.y_angle = self.x_angle=0
        self.distance = 20
        self.light = Light(GL_LIGHT0, (15, 5, 15, 1))

        self.sun = Planet(0.5,(1, 1, 0), self.planets['SUN'], 0)
        self.earth = Planet(0.4,(0.7, 0.8, 0.7), self.planets['EARTH'], 365)
        self.venus = Planet(0.35, (0.9, 0.5, 0.2), self.planets['VENUS'], 225)
        self.mercury = Planet(0.2, (0.5, 0.5, 0.5), self.planets['MERCURY'], 88)
        self.mars = Planet(0.3, (0.6, 0.2, 0.2), self.planets['MARS'], 687)

    def start(self):
        """Creates animated solar system using pygame engine and OpenGl to draw spheres and orbits"""
        pygame.init()
        pygame.font.init()
        pygame.display.set_mode((self.width, self.height), OPENGL | DOUBLEBUF)
        pygame.display.set_caption(self.title)

        glEnable(GL_CULL_FACE)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)

        glClearColor(.1, .1, .1, 1)
        glMatrixMode(GL_PROJECTION)
        aspect = self.width / self.height
        gluPerspective(40., aspect, 1., 40.)
        glMatrixMode(GL_MODELVIEW)

        clock = pygame.time.Clock()
        while True:
            clock.tick(self.fps)
            self.process_input()
            self.display()

    def process_input(self):
        """Handles events for arrow buttons and escape"""
        for event in pygame.event.get():
            if event.type == QUIT:
                self.quit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.quit()
            pressed = pygame.key.get_pressed()
            if pressed[K_LEFT]:
                self.y_angle -= 0.05
            if pressed[K_RIGHT]:
                self.y_angle += 0.05
            if pressed[K_DOWN]:
                self.x_angle -= 0.05
            if pressed[K_UP]:
                self.x_angle += 0.05

        self.y_angle %= math.pi * 2
        self.x_angle %= math.pi * 2

    def set_view_point(self):
        """Sets the position of the camera"""
        z = math.cos(self.y_angle) * math.cos(self.x_angle) * self.distance
        x = math.sin(self.y_angle) * math.cos(self.x_angle) * self.distance
        y = math.sin(self.x_angle) * self.distance
        gluLookAt(x, y, z, 0, 0, 0, 0, 1, 0)

    def display(self):
        """Renders light, planets, their path and pushes it to the screen"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        self.set_view_point()

        self.light.render()

        self.sun.render_planet(self.date)
        self.earth.render_planet(self.date)
        self.venus.render_planet(self.date)
        self.mercury.render_planet(self.date)
        self.mars.render_planet(self.date)

        self.earth.render_path()
        self.venus.render_path()
        self.mercury.render_path()
        self.mars.render_path()

        self.date = self.date + datetime.timedelta(days=1)

        pygame.display.flip()

    def quit(self):
        pygame.quit()
        sys.exit()


class Light(object):
    """ Handles the position of the light
        Args:
            light_id (int): Id of the light we are dealing with
            position (tuple): x,y,z coordinates of the light
            color(tuple): color of the light
    """
    def __init__(self,light_id, position, color=(1.,1.,1.,1.)):
        self.light_id = light_id
        self.position = position
        self.color = color

    def render(self):
        """Renders the light in the provided position"""
        light_id = self.light_id
        glLightfv(light_id, GL_POSITION, self.position)
        glLightfv(light_id, GL_DIFFUSE, self.color)
        glLightfv(light_id, GL_CONSTANT_ATTENUATION, 0.1)
        glLightfv(light_id, GL_LINEAR_ATTENUATION, 0.05)


class Planet(object):
    """ Handles Planets
        Args:
            radius (int): Radius of the planet
            color (tuple): the color of the planet
            planet (:obj:`~skyfield.vectorlib.VectorFunction`): skyfield instance that can calculate
                                                                position of the planet at the given time
            days (int): the number of days it takes the planet to go do the full lap
    """
    slices=40
    stacks=40

    def __init__(self, radius, color, planet, days):
        self.radius = radius
        self.color = color
        self.quadratic = gluNewQuadric()
        self.ts = load.timescale()
        self.planet = planet
        self.orbit = []
        self.days = days
        self.scale = 4

    def render_planet(self, date):
        """Draws the planet position at the given date
        Args:
            date (:obj:datetime): the date to calculate the position of the planet
        """
        glPushMatrix()
        position = tuple(pos*self.scale for pos in self.get_position(date))
        self.orbit.append(position)
        if len(self.orbit) > self.days+1:
            self.orbit.pop(0)
        glTranslatef(*position)
        glColor3f(*self.color);
        gluSphere(self.quadratic, self.radius, Planet.slices, Planet.stacks)
        glPopMatrix()

    def get_position(self, date):
        """Gets the barycentric coordinates of the planet at the given dateArgs:
            date (:obj:datetime): the date to calculate the position of the planet
        """
        x, y, z = self.planet.at(self.ts.utc(date.year, date.month, date.day)).position.au
        return x, y, z

    def render_path(self):
        """Draws the part of the orbit the planet made since the initial date"""
        glPushMatrix()
        glTranslatef(0,0,0)
        glDisable(GL_LIGHTING)
        glLineWidth(0.5)
        glColor3f(*self.color)
        for i in range(1, len(self.orbit)):
            glBegin(GL_LINE_LOOP)
            glVertex3f(*self.orbit[i-1])
            glVertex3f(*self.orbit[i])
            glEnd()
        glEnable(GL_LIGHTING)
        glPopMatrix()


if __name__ == "__main__":
    app = InnerSolarSystem()
    app.start()
