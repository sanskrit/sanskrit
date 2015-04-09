# -*- coding: utf-8 -*-
"""
    test.sandhi
    ~~~~~~~~~~~

    Tests joining and splitting words with sandhi rules.

    :license: MIT
"""

import pytest

from sanskrit import Context
from sanskrit.sandhi import Splitter, Joiner


@pytest.fixture
def simple_joiner():
    """A simple joiner."""
    return Joiner([
        ('a', 'i', 'e'),
        ('a', 'a', 'A'),
        ('a', 'A', 'A'),
        ('i', 'a', 'y a'),
        ('I', 'a', 'y a'),
        ('O', 'a', 'Av a'),
    ])


@pytest.fixture
def simple_splitter():
    """A simple splitter."""
    # "splits" blows up quickly, so the rule list is deliberately left small.
    return Splitter([
        ('a', 'a', 'A'),
        ('a', 'A', 'A'),
        ('O', 'a', 'Av a'),
    ])


class TestJoiner:
    EXTERNAL_JOINER_TESTS = [
        # Basic
        (('tasya', 'icCA'), 'tasyecCA'),
        (('tasya', 'aSvaH'), 'tasyASvaH'),
        (('tasya', 'Amoda'), 'tasyAmoda'),
        (('PalAni', 'apaSyat'), 'PalAny apaSyat'),
        (('kumArI', 'apaSyat'), 'kumAry apaSyat'),
        (('narO', 'apaSyat'), 'narAv apaSyat'),
        # Three terms
        (('tasya', 'aSvena', 'iti'), 'tasyASveneti'),
        # No change
        (('tam', 'eva'), 'tam eva'),
    ]

    INTERNAL_JOINER_TESTS = [
        (('nara', 'ina'), 'nareRa'),
    ]

    RETROFLEXION_TESTS = [
        ('narena', 'nareRa'),
        ('vAksu', 'vAkzu'),
        ('nisanna', 'nizaRRa'),
        ('agnInAm', 'agnInAm'),
        ('havisA', 'havizA'),
        ('rAmAyana', 'rAmAyaRa'),
    ]

    @pytest.mark.parametrize('terms,result', EXTERNAL_JOINER_TESTS)
    def test_join_external(self, simple_joiner, terms, result):
        assert simple_joiner.join(terms) == result

    @pytest.mark.parametrize('terms,result', INTERNAL_JOINER_TESTS)
    def test_join_internal(self, simple_joiner, terms, result):
        assert simple_joiner.join(terms, internal=True) == result

    @pytest.mark.parametrize('before,after', RETROFLEXION_TESTS)
    def test_internal_retroflexion(self, before, after):
        assert Joiner.internal_retroflex(before) == after


class TestSpliter:
    # "splits" blows up quickly, so these tokens are artificially small:
    SPLITTER_TESTS = [
        ('yAH', ['ya,aH', 'ya,AH'] +
            ['y,AH', 'yA,H', 'yAH,']),
        ('rAva', ['ra,ava', 'ra,Ava', 'rO,a'] +
            ['r,Ava', 'rA,va', 'rAv,a', 'rAva,'])
    ]

    @pytest.mark.parametrize('before,expected', SPLITTER_TESTS)
    def test_iter_splits(self, simple_splitter, before, expected):
        actual = set(','.join(x) for x in simple_splitter.iter_splits(before))
        assert actual == set(expected)
