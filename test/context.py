# -*- coding: utf-8 -*-
"""
test.context
~~~~~~~~~~~~

Tests the :class:`~sanskrit.context.Context` class.

:license: MIT and BSD
"""

import os
from sanskrit import Context
from . import TestCase, config as cfg

class ContextTestCase(TestCase):

    """Constructs a context in a variety of ways."""

    def compare_all(self, ctx):
        """Compare default config values to their expected values."""
        self.assertEqual(ctx.config['DATABASE_URI'], cfg.DATABASE_URI)
        self.assertEqual(ctx.config['DATA_PATH'], cfg.DATA_PATH)

        monier_xml_path = os.path.join(cfg.DATA_PATH, 'mw', 'monier.xml')
        monier_greek_path = os.path.join(cfg.DATA_PATH, 'mw', 'greek.yml')
        enum_path = os.path.join(cfg.DATA_PATH, 'misc', 'enum.yml')

        self.assertEqual(ctx.config['MONIER_XML_PATH'], monier_xml_path)

    def testFile(self):
        """Test creating from a filename."""
        path = os.path.join(os.path.dirname(__file__), 'config.py')
        ctx = Context(path)
        self.compare_all(ctx)

    def testModule(self):
        """Test creating from a module."""
        ctx = Context(cfg)
        self.compare_all(ctx)

    def testDict(self):
        """Test creating from a :class:`dict`."""
        config = dict(DATABASE_URI=cfg.DATABASE_URI, DATA_PATH=cfg.DATA_PATH)
        ctx = Context(config)
        self.compare_all(ctx)

    def testOverride(self):
        """Test overriding a default option"""
        config = dict(DATABASE_URI=cfg.DATABASE_URI, DATA_PATH=cfg.DATA_PATH,
                      MONIER_XML_PATH='foo')
        ctx = Context(config)
        self.assertEqual(ctx.config['MONIER_XML_PATH'], 'foo')
