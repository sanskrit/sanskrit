# -*- coding: utf-8 -*-
"""
test.sandhi
~~~~~~~~~~~

Tests joining and splitting words with sandhi rules.

:license: MIT and BSD
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sanskrit import Context
from sanskrit.db import setup as S  # ``as S`` avoids problems with nose
from sanskrit.schema import SandhiRule
from sanskrit.language import sandhi

from . import TestCase, config as cfg

class SandhiTestCase(TestCase):

    """Tests basic sandhi operations."""

    def setUp(self):
        """Load all sandhi rules into the database."""
        s = str.split
        self.two_split = [
            (s('kim akurvata'), 'kim akurvata'),
            (s('tat hita'), 'tad Dita'),
            (s('kanyA fcCati'), 'kanyarcCati'),
            (s('PalAni alaBat'), 'PalAny alaBat'),
            (s('yogin arjuna'), 'yoginn arjuna'),
            (s('narEs agacCat'), 'narEr agacCat'),
        ]
        self.three_split = [
            (s('pARqavAS ca eva'), 'pARqavAS cEva'),
            (['tasmin', 'Pale', 'iti'], 'tasmin Pala iti'),
            (['te', sandhi.Exempt('Pale'), 'iti'], 'te Pale iti'),
        ]

        ctx = Context(cfg)
        session = ctx.session_class()
        S.create_tables(ctx)
        S.add_sandhi(session, ctx)

        self.sandhi = sandhi.Sandhi()
        self.sandhi.load(ctx)

    def test_join(self):
        """Test joining chunks together."""
        for chunks, joined in self.two_split + self.three_split:
            self.assertEqual(self.sandhi.join(*chunks), joined)

    def test_splits(self):
        """Test splitting chunks apart."""
        for chunks, joined in self.two_split:
            splits = list(self.sandhi.splits(joined.replace(' ', '')))
            self.assertIn(tuple(chunks), splits)
