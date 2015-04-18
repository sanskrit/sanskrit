# -*- coding: utf-8 -*-
"""
test.schema
~~~~~~~~~~~

Tests linguistic schema on various data.

:license: MIT and BSD
"""

from sanskrit import Context
from sanskrit import setup
from sanskrit.schema import *

from . import TestCase, config as cfg


class SchemaTestCase(TestCase):

    """Creates a new database before every test. This also provides some
    helper code.
    """

    def setUp(self):
        """Create a new database."""
        self.ctx = Context(cfg)
        self.ctx.create_all()
        self.session = self.ctx.session
        setup.add_enums(self.ctx)
        self.enum = setup.ENUM

    def add_root(self, name):
        """Add a root with the given name.

        :param name: the name of the root.
        """
        root = Root(name=name)
        self.session.add(root)
        self.session.commit()
        return root


class EnumTestCase(SchemaTestCase):

    """Tests the "enumerated" classes."""

    def test_enum_names(self):
        """Test enum values."""
        def q(cls, id):
            return self.session.query(cls).filter(cls.id == id).one()

        enum = self.enum
        third = q(Person, enum['person']['3'])
        dual = q(Number, enum['number']['d'])
        parasmaipada = q(Voice, enum['voice']['para'])
        masculine = q(Gender, enum['gender']['m'])
        dative = q(Case, enum['case']['4'])

        assert third.abbr == '3'
        assert dual.abbr == 'd'
        assert parasmaipada.abbr == 'para'
        assert masculine.abbr == 'm'
        assert dative.abbr == '4'


class FormTestCase(SchemaTestCase):

    """Tests a variety of linguistic forms."""

    def test_verb(self):
        """Test verbs."""
        session = self.session
        enum = self.enum

        p, n, m, v = (enum['person']['3'], enum['number']['s'],
                      enum['mode']['pres'], enum['voice']['para'])

        root = self.add_root('kf')
        p1 = Paradigm(root_id=root.id, vclass_id=enum['vclass']['5'],
                      voice_id=enum['voice']['ubhaya'])
        p2 = Paradigm(root_id=root.id, vclass_id=enum['vclass']['8'],
                      voice_id=enum['voice']['ubhaya'])
        session.add_all([p1, p2])
        session.flush()

        verb = Verb(root=root, name='karoti', vclass_id=enum['vclass']['5'],
                    person_id=p, number_id=n, mode_id=m, voice_id=v)
        session.add(verb)
        session.commit()

        assert root.id is not None
        assert p1.id is not None
        assert p2.id is not None
        assert verb.id is not None
        session.close()

        # Root
        root = session.query(Root).first()
        vclasses = [x.id for x in root.vclasses]
        assert root.name == 'kf'
        assert vclasses == [enum['vclass']['5'], enum['vclass']['8']]

        # Verb
        verb = session.query(Verb).first()
        assert verb.name == 'karoti'
        assert verb.person_id == p
        assert verb.number_id == n
        assert verb.mode_id == m
        assert verb.voice_id == v

        # Root-verb associations
        assert root.id == verb.root_id
        assert verb.root.name == 'kf'

    def test_noun(self):
        """Test nouns."""
        session = self.session
        enum = self.enum

        stem = NounStem(name='nara')
        session.add(stem)
        session.flush()

        noun = Noun(stem=stem, name='narasya', gender_id=enum['gender']['m'],
                    case_id=enum['case']['6'], number_id=enum['number']['s'])
        session.add(noun)
        session.commit()

        assert stem.id is not None
        assert noun.id is not None
        session.close()

        # Stem
        stem = session.query(Stem).first()
        assert stem.pos_id == Tag.NOUN
        assert stem.name == 'nara'

        # Noun
        noun = session.query(Noun).first()
        assert noun.pos_id == Tag.NOUN
        assert noun.name == 'narasya'
        assert noun.gender_id == enum['gender']['m']
        assert noun.case_id == enum['case']['6']
        assert noun.number_id == enum['number']['s']

        # Stem-noun associtaions
        assert stem.id == noun.stem_id

    def test_indeclinable(self):
        """Test indeclinables."""
        session = self.session

        ind = Indeclinable(name='ca')
        session.add(ind)
        session.commit()
        session.close()

        ind = session.query(Indeclinable).first()
        assert ind.id is not None
        assert ind.pos_id == Tag.INDECLINABLE
        assert ind.name == 'ca'

    def test_infinitive(self):
        """Test infinitives."""
        session = self.session

        root = self.add_root('gam')
        inf = Infinitive(name='gantum', root_id=root.id)
        session.add(inf)
        session.commit()
        session.close()

        inf = session.query(Infinitive).first()
        assert inf.id is not None
        assert inf.pos_id == Tag.INFINITIVE
        assert inf.name == 'gantum'
        assert inf.root.name == 'gam'

    def test_participle(self):
        """Test participles."""
        session = self.session
        enum = self.enum

        g, c, n = (enum['gender']['m'], enum['case']['2'], enum['number']['s'])

        root = self.add_root('car')
        part_stem = ParticipleStem(name='carat', root_id=root.id,
                                   mode_id=enum['mode']['pres'],
                                   voice_id=enum['voice']['para'])
        session.add(part_stem)
        session.flush()

        part = Participle(stem=part_stem, name='carantam', gender_id=g,
                          case_id=c, number_id=n)
        session.add(part)
        session.commit()
        session.close()

        part = session.query(Participle).first()
        assert part.id is not None
        assert part.name == 'carantam'
        assert part.root.name == 'car'
        assert part.stem.name == 'carat'
        assert part.gender_id == g
        assert part.case_id == c
        assert part.number_id == n

    def test_prefixed_verb(self):
        """Test prefixed verbs."""
        session = self.session
        enum = self.enum

        p, n, m, v = (enum['person']['3'], enum['number']['s'],
                      enum['mode']['pres'], enum['voice']['para'])

        root = self.add_root('gam')
        p1 = VerbPrefix(name='upa')
        p2 = VerbPrefix(name='sam')
        session.add_all([p1, p2])
        session.flush()

        proot = PrefixedRoot(name='upasaMgam', basis_id=root.id)
        proot.prefixes = [p1, p2]
        session.add(proot)
        session.flush()

        verb = Verb(name='upasamagamat', root_id=proot.id,
                person_id=p, number_id=n, mode_id=m, voice_id=v)
        session.add(verb)
        session.commit()

        assert root.id is not None
        assert proot.id is not None
        assert p1.id is not None
        assert p2.id is not None
        assert verb.id is not None
        session.close()

        verb = session.query(Verb).first()
        prefixes = [x.name for x in verb.root.prefixes]
        assert verb.root.name == 'upasaMgam'
        assert prefixes == ['upa', 'sam']

    def test_modified_verb(self):
        """Test modified verbs."""
        session = self.session
        enum = self.enum

        mod = enum['modification']['caus']
        p, n, m, v = (enum['person']['3'], enum['number']['s'],
                     enum['mode']['impv'], enum['voice']['para'])

        root = self.add_root('gam')
        mroot = ModifiedRoot(name='gamaya', basis_id=root.id)
        mroot.modifications = [session.query(Modification).get(mod)]
        session.add(mroot)
        session.flush()

        verb = Verb(name='gamayatu', root_id=mroot.id,
                person_id=p, number_id=n, mode_id=m, voice_id=v)
        session.add(verb)
        session.commit()

        assert root.id is not None
        assert mroot.id is not None
        assert verb.id is not None
        session.close()

        verb = session.query(Verb).first()
        mods = [x.id for x in verb.root.modifications]
        assert verb.root.name == 'gamaya'
        assert verb.root.basis.name == 'gam'
        assert mods == [mod]

    def test_prefixed_modified_verb(self):
        """Test modified verbs with prefixes."""
        session = self.session
        enum = self.enum

        mod = enum['modification']['caus']
        p, n, m, v = (enum['person']['3'], enum['number']['s'],
                      enum['mode']['opt'], enum['voice']['para'])

        root = self.add_root('gam')
        p1 = VerbPrefix(name='upa')
        p2 = VerbPrefix(name='sam')
        session.add_all([p1, p2])
        session.flush()

        pmroot = PrefixedModifiedRoot(name='upasaMgamaya', basis_id=root.id)
        pmroot.prefixes = [p1, p2]
        pmroot.modifications = [session.query(Modification).get(mod)]
        session.add(pmroot)
        session.flush()

        verb = Verb(name='upasaMgamayet', root_id=pmroot.id,
                person_id=p, number_id=n, mode_id=m, voice_id=v)
        session.add(verb)
        session.commit()

        assert root.id is not None
        assert pmroot.id is not None
        assert verb.id is not None
        session.close()
        verb = session.query(Verb).first()
        mods = [x.id for x in verb.root.modifications]
        prefixes = [x.name for x in verb.root.prefixes]
        assert verb.root.name == 'upasaMgamaya'
        assert verb.root.basis.name == 'gam'
        assert mods == [mod]
        assert prefixes == ['upa', 'sam']
