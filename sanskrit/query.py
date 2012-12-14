# -*- coding: utf-8 -*-
"""
    sanskrit.language.query
    ~~~~~~~~~~~~~~~~~~~~~~~

    A simple interface for querying Sanskrit linguistic data.

    :license: MIT and BSD
"""

from .schema import *


class SimpleQuery(object):

    """A simple wrapper for database access."""

    def __init__(self, ctx):
        self.ctx = ctx
        self.session = ctx.session_class()

    def pronoun(self, stem_name, gender):
        """Query for pronouns.

        :param stem_name: the stem name
        :param gender: the pronoun gender
        """
        enum_id = self.ctx.enum_id
        enum_abbr = self.ctx.enum_abbr
        session = self.session

        stem = session.query(PronounStem)\
                      .filter(PronounStem.name == stem_name)\
                      .first()

        stem_id = stem.id
        gender_id = enum_id['gender'][gender]

        returned = {}
        results = session.query(Pronoun)\
                         .filter(Pronoun.stem_id == stem_id)\
                         .filter(Pronoun.gender_id == gender_id)
        for pronoun in results:
            case = enum_abbr['case'][pronoun.case_id]
            number = enum_abbr['number'][pronoun.number_id]
            returned[(case, number)] = pronoun.name

        session.close()
        return returned

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
