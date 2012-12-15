# -*- coding: utf-8 -*-
"""
    sanskrit.language.query
    ~~~~~~~~~~~~~~~~~~~~~~~

    A simple interface for querying Sanskrit linguistic data.

    :license: MIT and BSD
"""

from .schema import *
from .language.generator import Generator


class SimpleQuery(object):

    """A simple API for database access."""

    def __init__(self, ctx):
        self.ctx = ctx
        self.session = ctx.session_class()
        self.generator = Generator(ctx)

    def _fetch_nominal_paradigm(self, stem_id, gender_id):
        """Fetch a nominal paradigm from the database."""
        enum_abbr = self.ctx.enum_abbr

        results = self.session.query(Nominal)\
                              .filter(Nominal.stem_id == stem_id)\
                              .filter(Nominal.gender_id == gender_id)

        returned = {}
        for nominal in results:
            case = enum_abbr['case'][nominal.case_id]
            number = enum_abbr['number'][nominal.number_id]
            returned[(case, number)] = nominal.name

        return returned

    def _nominal_stem(self, stem_name, stem_cls=None):
        """Fetch a nominal stem from the database."""
        stem_cls = stem_cls or Stem
        stem = self.session.query(stem_cls)\
                           .filter(stem_cls.name == stem_name)\
                           .first()
        return stem

    def noun(self, stem_name, gender):
        """Query for nouns.

        :param stem_name: the stem name
        :param gender: the noun gender
        """
        stem = self._nominal_stem(stem_name, NounStem)
        if stem is None:
            return {}

        return self.generator.nominal_paradigm(stem_name, gender)

    def pronoun(self, stem_name, gender):
        """Query for pronouns.

        :param stem_name: the stem name
        :param gender: the pronoun gender
        """
        stem = self._nominal_stem(stem_name, PronounStem)
        if stem is None:
            return {}

        gender_id = self.ctx.enum_id['gender'][gender]
        return self._fetch_nominal_paradigm(stem.id, gender_id)

    def verb(self, root_name, mode, voice, vclass=None):
        """Query for inflected verbs.

        :param root_name: the verb root
        :param mode: the verb mode
        :param voice: the verb voice
        :param vclass: the verb class to use. This can be used to
                       distinguish between homophonous roots, such as
                       'kR' ("do") and 'kR' ("praise").
        """
        enum_id = self.ctx.enum_id
        enum_abbr = self.ctx.enum_abbr
        session = self.session

        root = session.query(Root).filter(Root.name == root_name).first()
        root_id = root.id
        mode_id = enum_id['mode'][mode]
        voice_id = enum_id['voice'][voice]

        returned = {}
        results = session.query(Verb)\
                         .filter(Verb.root_id == root_id)\
                         .filter(Verb.mode_id == mode_id)\
                         .filter(Verb.voice_id == voice_id)
        for verb in results:
            person = enum_abbr['person'][verb.person_id]
            number = enum_abbr['number'][verb.number_id]
            returned[(person, number)] = verb.name

        session.close()
        return returned
