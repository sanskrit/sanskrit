# -*- coding: utf-8 -*-
"""
test.betacode
~~~~~~~~~~~~~

Tests Greek transliteration.

:license: MIT and BSD
"""

from __future__ import unicode_literals

from sanskrit.transliterate import betacode as B
from unittest import TestCase


class BetaTestCase(TestCase):
    """Ordinary :class:`~unittest.TestCase`"""

    def test_betacode(self):
        data = [
            ('ἐν', 'E)N'),
            ('ὁ, οἱ', 'O(, OI('),
            ('πρός', 'PRO/S'),
            ('τῶν', 'TW=N'),
            ('πρὸς', 'PRO\S'),
            ('προϊέναι', 'PROI+E/NAI'),
            ('τῷ', 'TW=|'),
            ('μοῦσα', 'MOU=SA'),
            ('χέϝω', 'XE/VW'),
            ('μῆνιν ἄειδε θεὰ Πηληϊάδεω Ἀχιλῆος',
                "MH=NIN A)/EIDE QEA\ *PHLHI+A/DEW *)AXILH=OS"),
        ]
        for greek, beta in data:
            self.assertEqual(greek, B.transliterate(beta))
