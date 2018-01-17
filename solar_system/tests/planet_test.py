import os
import datetime
from unittest import TestCase
from skyfield.api import load
from solar_system import Planet


class TestPlanet(TestCase):

    def setUp(self):
        self.planets = load('de421.bsp')


    def test_is_correct_position(self):
        planet = Planet(0.4,(0.7, 0.8, 0.7), self.planets['EARTH'], 365)
        x, y, z = planet.get_position(datetime.datetime(1981, 10, 10))
        self.assertEqual("0.964", "%.3f" % x)
        self.assertEqual("0.270", "%.3f" % y)
        self.assertEqual("0.117", "%.3f" % z)