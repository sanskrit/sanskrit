# -*- coding: utf-8 -*-
"""
test.sounds
~~~~~~~~~~~

Tests various functions for Sanskrit sounds.

:license: MIT and BSD
"""

from sanskrit.language import sounds
from . import TestCase

class CleanTestCase(TestCase):
    def test(self):
        func = sounds.clean
        self.assertEqual('kaTam idam', func('kaTam! idam...'))
        self.assertEqual('kTmdm', func('ka!!!Tamida23m//', sounds.CONSONANTS))


class NumSyllablesTestCase(TestCase):

    def test_simple(self):
        """Test some simple syllables."""
        func = sounds.num_syllables
        self.assertEqual(1, func('a'))
        self.assertEqual(1, func('I'))
        self.assertEqual(1, func('zwre'))
        self.assertEqual(1, func('uM'))

    def test_long(self):
        """Test longer phrases."""
        func = sounds.num_syllables
        self.assertEqual(8, func('Darmakzetre kurukzetre'))


class MeterTestCase(TestCase):

    def test_simple(self):
        """Test some simple syllables."""
        for v in sounds.SHORT_VOWELS:
            self.assertEqual('.', ''.join(sounds.meter(v)))
        for v in sounds.LONG_VOWELS:
            self.assertEqual('_', ''.join(sounds.meter(v)))
        for groups in ['aM naH yuG']:
            self.assertEqual('_', ''.join(sounds.meter(v)))

    def test_meghaduta(self):
        """Test some lines from the Meghaduta."""
        verse = """
        kaScitkAntAvirahaguruRA svADikArapramattaH
        SApenAstaMgamitamahimA varzaBogyeRa BartuH .
        yakzaScakre janakatanayAsnAnapuRyodakezu
        snigDacCAyAtaruzu vasatiM rAmagiryASramezu .. 1 ..
        """

        mandakranta = '____.....__.__.__'
        for line in verse.strip().splitlines():
            scan = sounds.meter(line)
            scan[-1] = '_'
            self.assertEqual(mandakranta, ''.join(scan))
