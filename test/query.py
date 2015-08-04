# -*- coding: utf-8 -*-
"""
test.query
~~~~~~~~~~

Tests something.

:license: MIT and BSD
"""

from sanskrit import Context
from sanskrit import setup as S  # ``as S`` avoids problems with nose
from sanskrit.query import SimpleQuery
from sanskrit.schema import *

from . import TestCase, config as cfg

ctx = Context(cfg)
db_built = False


class QueryTestCase(TestCase):

    def setUp(self):
        """Initialize the database if it doesn't exist."""
        global db_built

        if not db_built:
            ctx.drop_all()
            ctx.create_all()
            S.run(ctx)
            db_built = True

    def verify(self, actual, expected):
        for k in expected:
            self.assertIn(k, actual)
            self.assertEqual(actual[k], expected[k])

    def test_pronoun(self):
        expected = {
            ('1', 's'): 'saH',
            ('1', 'd'): 'tO',
            ('1', 'p'): 'te',
        }

        Q = SimpleQuery(ctx)
        name_actual = Q.pronoun('tad', 'masculine')
        abbr_actual = Q.pronoun('tad', 'm')
        self.verify(name_actual, expected)
        self.verify(abbr_actual, expected)
        self.assertEqual(len(name_actual), 3)

    def test_noun(self):
        expected = {
            ('1', 's'): 'gajaH',
            ('1', 'd'): 'gajO',
            ('1', 'p'): 'gajAH',
        }

        Q = SimpleQuery(ctx)
        name_actual = Q.noun('gaja', 'masculine')
        abbr_actual = Q.noun('gaja', 'm')
        self.verify(name_actual, expected)
        self.verify(abbr_actual, expected)
        self.assertEqual(len(name_actual), 24)

    def test_verb(self):
        expected = {
            ('3', 's'): 'gacCati',
            ('3', 'd'): 'gacCataH',
            ('3', 'p'): 'gacCanti',
            ('2', 's'): 'gacCasi',
            ('2', 'd'): 'gacCaTaH',
            ('2', 'p'): 'gacCaTa',
            ('1', 's'): 'gacCAmi',
            ('1', 'd'): 'gacCAvaH',
            ('1', 'p'): 'gacCAmaH',
        }

        Q = SimpleQuery(ctx)
        name_actual = Q.verb('gam', 'present', 'parasmaipada')
        abbr_actual = Q.verb('gam', 'pres', 'para')
        self.verify(name_actual, expected)
        self.verify(abbr_actual, expected)
