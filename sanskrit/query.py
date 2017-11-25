# -*- coding: utf-8 -*-
"""
    sanskrit.language.query
    ~~~~~~~~~~~~~~~~~~~~~~~

    A simple interface for querying Sanskrit linguistic data.

    :license: MIT and BSD
"""

from collections import defaultdict
import six
from . import sounds
from .generate import NominalGenerator
from .schema import *


class SimpleQuery(object):

    """A simple API for database access."""

    def __init__(self, ctx):
        self.ctx = ctx
        self.session = ctx.session
        self.nominal = NominalGenerator(ctx)

        # Store IDs of irregular stems
        irreg = self.session.query(StemIrregularity) \
                    .filter(StemIrregularity.fully_described == True)

        self.irregular_stems = set([x.id for x in irreg])
        self.session.remove()

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

    def _simplify(self, forms):
        """Simplify the given forms by applying consonant reduction."""
        for parse, name in six.iteritems(forms):
            forms[parse] = sounds.Term(name).simplify()

    def noun(self, stem_name, gender):
        """Query for nouns.

        :param stem_name: the stem name
        :param gender: the noun gender
        """
        stem = self._nominal_stem(stem_name, NominalStem)
        if stem is None:
            return {}

        if stem.id in self.irregular_stems:
            gender_id = self.ctx.enum_id['gender'][gender]
            returned = self._fetch_nominal_paradigm(stem.id, gender_id)
        elif stem:
            returned = self.nominal.paradigm(stem_name, gender)

        self._simplify(returned)
        return returned

    def pronoun(self, stem_name, gender):
        """Query for pronouns.

        :param stem_name: the stem name
        :param gender: the pronoun gender
        """
        stem = self._nominal_stem(stem_name, PronounStem)
        if stem is None:
            return {}

        gender_id = self.ctx.enum_id['gender'][gender]
        returned = self._fetch_nominal_paradigm(stem.id, gender_id)

        self._simplify(returned)
        return returned

    def verb(self, root_name, mode, voice, vclass=None, **kw):
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

        roots = session.query(Root).filter(Root.name == root_name)
        roots_id = [r.id for r in roots]
        mode_id = enum_id['mode'][mode]
        voice_id = enum_id['voice'][voice]

        returned = {}
        results = session.query(Verb)\
                         .filter(Verb.root_id.in_(roots_id))\
                         .filter(Verb.mode_id == mode_id)\
                         .filter(Verb.voice_id == voice_id)
        for verb in results:
            person = enum_abbr['person'][verb.person_id]
            number = enum_abbr['number'][verb.number_id]
            returned[(person, number)] = verb.name

        session.close()
        self._simplify(returned)
        return returned

    def verb_summary(self, root_name, vclass=None):
        """Query for a summary of a verb's behavior.

        The function returns the following information:

        - the root ID
        - the 3rd. sg. forms of all verbs produced from the plain root
        - the stems of all participles produced from the plain root

        :param root: the verb root
        :param vclass: the verb class to use. This can be used to
                       distinguish between homophonous roots, such as
                       'kR' ("do") and 'kR' ("praise").
        """
        verbs = defaultdict(list)
        participles = defaultdict(list)

        ctx = self.ctx
        session = self.session

        # abbr -> ID
        ei_person = ctx.enum_id['person']
        ei_number = ctx.enum_id['number']

        # ID -> abbr
        ea_mode = ctx.enum_abbr['mode']
        ea_voice = ctx.enum_abbr['voice']

        # Root
        root = session.query(Root).filter(Root.name == root_name).first()
        if root is None:
            return {}
        root_id = root.id

        # Verbs
        results = session.query(Verb).filter(Verb.root_id == root_id) \
                         .filter(Verb.person_id == ei_person['3']) \
                         .filter(Verb.number_id == ei_number['s'])\

        for r in results:
            mode = ea_mode[r.mode_id]
            voice = ea_voice[r.voice_id]
            verbs[(mode, voice)].append(r.name)

        # Participles
        results = session.query(ParticipleStem) \
                         .filter(ParticipleStem.root_id == root_id)

        for r in results:
            mode = ea_mode[r.mode_id]
            voice = ea_voice[r.voice_id]
            participles[(mode, voice)].append(r.name)

        session.close()
        return {
            'root_id': root_id,
            'verbs': verbs,
            'participles': participles,
        }
