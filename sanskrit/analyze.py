# -*- coding: utf-8 -*-
"""
    sanskrit.analyze
    ~~~~~~~~~~~~~~~~

    Code for *analyzing* Sanskrit forms, i.e. finding the basic lexical
    forms that produced them and specifying the word's inflectional
    information.

    :license: MIT
"""

from collections import defaultdict, namedtuple

from . import sounds, util
from .schema import *


Ending = namedtuple('Ending', ['name', 'length', 'stem_type', 'gender_id',
                               'case_id', 'number_id', 'compounded',
                               'is_consonant_stem'])


class Analyzer(object):

    """analyzer"""

    def __init__(self):
        raise NotImplementedError

    def analyze(self, token):
        raise NotImplementedError


class SimpleAnalyzer(Analyzer):

    """A simple analyzer for Sanskrit words. The analyzer is simple
    for a few reasons:

    - It doesn't do any caching.
    - It uses an ORM instead of raw SQL queries.
    - Its output is always "well-formed." For example, neuter nouns can
      take only neuter endings.

    This analyzer is best used when memory is at a premium and speed is
    a secondary concern (e.g. when on a web server).
    """

    def __init__(self, ctx):
        self.ctx = ctx
        self.session = ctx.session

        self.nominal_endings = util.HashTrie()
        for e in self.session.query(NominalEnding):
            stem_type = e.stem_type
            is_cons = (stem_type == NominalEnding.CONSONANT_STEM_TYPE)
            if e.stem_type == "_": 
                e.stem_type = ""
                is_cons = True

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
            if 'n' in e.name:
                # TODO: do this more rigorously
                reversed_name = e.name.replace('n', 'R')
                data['name'] = reversed_name
                self.nominal_endings[reversed_name[::-1]] = Ending(**data)


        self.session.remove()

    def _analyze_as_form(self, word):
        """
        Analyze a word by searching for an exact match in the database.

        :param word: the word to analyze
        """
        session = self.session
        results = session.query(Form).filter(Form.name == word).all()
        return results

    def _analyze_as_stem(self, word):
        """
        Analyze a word by searching for the nominal stems that might
        have produced it.

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
                # Stem must exist and end in a consonant.
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

        if not stem_endings_map:
            return []

        # Check which of these stems are viable
        stems = session.query(Stem) \
                       .filter(Stem.name.in_(stem_endings_map.keys()))

        # Reattach endings to viable stems
        for stem in stems:
            name = stem.name

            # For nouns, disregard endings that don't match the stem's
            # genders.
            # TODO: fix semantics of this
            if stem.pos_id == Tag.NOMINAL:
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

    def analyze(self, word):
        """Return all possible solutions for the given word. Any ORM
        objects used in these solutions will be in a detached state.

        :param word: the word to analyze. This should be a complete
                     word, or what Panini would call a *pada*.
        """
        returned = self._analyze_as_form(word)
        returned.extend(self._analyze_as_stem(word))
        return returned
