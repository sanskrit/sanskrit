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

db_built = False


class QueryTestCase(TestCase):

    def setUp(self):
        """Initialize the database if it doesn't exist."""
        ctx = self.ctx = Context(cfg)
        global db_built

        if not db_built:
            ctx.drop_all()
            ctx.create_all()
            S.run(ctx)
            db_built = True

    def test_verb(self):
        expected = {
            ('3', 's'): 'gacCati',
            ('3', 'd'): 'gacCatas',
            ('3', 'p'): 'gacCanti',
            ('2', 's'): 'gacCasi',
            ('2', 'd'): 'gacCaTas',
            ('2', 'p'): 'gacCaTa',
            ('1', 's'): 'gacCAmi',
            ('1', 'd'): 'gacCAvas',
            ('1', 'p'): 'gacCAmas',
        }

        Q = SimpleQuery(self.ctx)
        name_actual = Q.verb('gam', 'present', 'parasmaipada')
        abbr_actual = Q.verb('gam', 'pres', 'P')
        self.assertEqual(name_actual, expected)
        self.assertEqual(abbr_actual, expected)
