# -*- coding: utf-8 -*-
"""
    sanskrit.analyze
    ~~~~~~~~~~~~~~~~

    Analyze a Sanskrit form and break it down to its basic parts.

    :license: MIT and BSD
"""

from collections import defaultdict, namedtuple

from . import sounds, util
from .schema import *


Ending = namedtuple('Ending', ['name', 'length', 'stem_type', 'gender_id',
                               'case_id', 'number_id', 'compounded',
                               'is_consonant_stem'])

Nominal = namedtuple('Nominal', ['name', 'pos_id', 'stem', 'gender_id',
                                 'case_id', 'number_id', 'compounded'])


class SimpleAnalyzer(object):

    """A simple analyzer for Sanskrit words. The analyzer is simple
    for a few reasons:

    - It doesn't do any caching.
    - It uses an ORM instead of raw SQL queries.
    - Its output is always "well-formed." For example, neuter nouns can
      take only neuter endings.

    This analyzer is best used when memory is at a premium and speed is
    a secondary concern (e.g. when on a web server).
    """

    def __init__(self, ctx, session=None):
        self.ctx = ctx
        self.session = session or ctx.session

        self.nominal_endings = util.HashTrie()
        for e in self.session.query(NominalEnding):
            stem_type = e.stem_type
            is_cons = (stem_type == NominalEnding.CONSONANT_STEM_TYPE)

            data = {
                'name': e.name,
                'stem_type': e.stem_type,
                'length': len(e.name),
                'gender_id': e.gender_id,
                'case_id': e.case_id,
                'number_id': e.number_id,
                'compounded': e.compounded,
                'is_consonant_stem': is_cons,
                }
            self.nominal_endings[e.name[::-1]] = Ending(**data)

        self.session.remove()

    def analyze(self, word):
        """Return all possible solutions for the given word. Any ORM
        objects used in these solutions will be in a detached state.

        :param word: the word to analyze. This should be a completeh
                     word, or what Panini would call a *pada*.
        """
        returned = []
        returned.extend(self.analyze_word(word))
        returned.extend(self.analyze_nominal(word))
        returned.extend(self.analyze_verb(word))

        return returned

    def analyze_word(self, word):
        """
        Analyze an arbitrary word.

        :param word: the word to analyze
        """
        session = self.session
        results = session.query(Form).filter(Form.name == word).all()
        return results

    def analyze_nominal(self, word):
        """
        Analyze a nominal word.

        :param word: the word to analyze
        """
        session = self.session
        gender_set = self.ctx.gender_set
        returned = []

        # Find all stems that could produce this word. Some of these
        # stems might not exist.
        stem_endings_map = defaultdict(set)
        endings = self.nominal_endings[word[::-1]]
        for e in endings:
            truncated_stem = word[:-e.length] or word
            if e.is_consonant_stem:
                # Use some basic
                if not truncated_stem:
                    continue
                if truncated_stem[-1] in sounds.VOWELS:
                    continue
                if truncated_stem in sounds.CONSONANTS:
                    continue
                stem = truncated_stem
            else:
                stem = truncated_stem + e.stem_type

            stem_endings_map[stem].add(e)

        # Check which of these stems are viable
        stems = session.query(Stem) \
                       .filter(Stem.name.in_(stem_endings_map.keys()))

        # Reattach endings to viable stems
        for stem in stems:
            name = stem.name

            # For nouns, disregard endings that don't match the stem's
            # genders.
            if stem.pos_id == Tag.NOUN:
                stem_genders = gender_set[stem.genders_id]
                endings = (e for e in stem_endings_map[name]
                           if e.gender_id in stem_genders)
            else:
                endings = stem_endings_map[name]

            for e in endings:
                datum = {
                    'name': word,
                    'pos_id': stem.pos_id,
                    'stem': stem,
                    'gender_id': e.gender_id,
                    'case_id': e.case_id,
                    'number_id': e.number_id,
                    'compounded': e.compounded,
                    }
                returned.append(Nominal(**datum))

        return returned

    def analyze_verb(self, word):
        """
        Analyze a verb

        :param word: the word to analyze
        """
        returned = []
        return returned
