# -*- coding: utf-8 -*-
"""
test.sounds
~~~~~~~~~~~

Tests various functions for Sanskrit sounds.

:license: MIT and BSD
"""

from sanskrit import sounds
from . import TestCase


class CleanTestCase(TestCase):
    def test(self):
        func = sounds.clean
        self.assertEqual('kaTam idam', func('kaTam! idam...'))
        self.assertEqual('kTmdm', func('ka!!!Tamida23m//', sounds.CONSONANTS))


class TransformTestCase(TestCase):
    def test_aspirate(self):
        func = sounds.aspirate
        self.assertEqual('K', func('k'))
        self.assertEqual('J', func('J'))
        self.assertEqual('a', func('a'))

    def test_deaspirate(self):
        func = sounds.deaspirate
        self.assertEqual('k', func('k'))
        self.assertEqual('j', func('J'))
        self.assertEqual('a', func('a'))

    def test_voice(self):
        func = sounds.voice
        self.assertEqual('b', func('p'))
        self.assertEqual('Q', func('Q'))
        self.assertEqual('a', func('a'))

    def test_devoice(self):
        func = sounds.devoice
        self.assertEqual('k', func('k'))
        self.assertEqual('C', func('J'))
        self.assertEqual('a', func('a'))

    def test_nasalize(self):
        func = sounds.nasalize
        self.assertEqual('N', func('k'))
        self.assertEqual('m', func('p'))
        self.assertEqual('a', func('a'))

    def test_dentalize(self):
        func = sounds.dentalize
        self.assertEqual('t', func('w'))
        self.assertEqual('s', func('z'))
        self.assertEqual('a', func('a'))

    def test_simplify(self):
        func = sounds.simplify
        self.assertEqual('k', func('G'))
        self.assertEqual('w', func('j'))
        self.assertEqual('a', func('a'))

    def test_guna(self):
        func = sounds.guna
        data = zip('a A i I u U  f  F  x  X e E o O'.split(),
                   'a A e e o o ar ar al al e E o O'.split())

        for data, output in data:
            self.assertEqual(output, func(data))

    def test_vrddhi(self):
        func = sounds.vrddhi
        data = zip('a A i I u U  f  F  x  X e E o O'.split(),
                   'A A E E O O Ar Ar Al Al E E O O'.split())

        for data, output in data:
            self.assertEqual(output, func(data))


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
