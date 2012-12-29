# -*- coding: utf-8 -*-
"""
test.schema
~~~~~~~~~~~

Tests linguistic schema on various data.

:license: MIT and BSD
"""

from sanskrit import Context
from sanskrit import setup as S  # ``as S`` avoids problems with nose
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
        S.add_enums(self.ctx)
        self.enum = S.ENUM

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
        def q(obj):
            return self.session.query(obj).all()

        print [x.__dict__ for x in q(Voice)]
        enum = self.enum
        third = next(x for x in q(Person) if x.id == enum['person']['3'])
        dual = next(x for x in q(Number) if x.id == enum['number']['d'])
        parasmaipada = next(x for x in q(Voice) if x.id == enum['voice']['P'])
        masculine = next(x for x in q(Gender) if x.id == enum['gender']['m'])
        dative = next(x for x in q(Case) if x.id == enum['case']['4'])

        self.assertEqual(third.abbr, '3')
        self.assertEqual(dual.abbr, 'd')
        self.assertEqual(parasmaipada.abbr, 'P')
        self.assertEqual(masculine.abbr, 'm')
        self.assertEqual(dative.abbr, '4')


class FormTestCase(SchemaTestCase):

    """Tests a variety of linguistic forms."""

    def test_verb(self):
        """Test verbs."""
        session = self.session
        enum = self.enum

        p, n, m, v = (enum['person']['3'], enum['number']['s'],
                      enum['mode']['pres'], enum['voice']['P'])

        root = self.add_root('kf')
        p1 = Paradigm(root_id=root.id, vclass_id=enum['vclass']['5'],
                      voice_id=enum['voice']['U'])
        p2 = Paradigm(root_id=root.id, vclass_id=enum['vclass']['8'],
                      voice_id=enum['voice']['U'])
        session.add_all([p1, p2])
        session.flush()

        verb = Verb(root=root, name='karoti', vclass_id=enum['vclass']['5'],
                    person_id=p, number_id=n, mode_id=m, voice_id=v)
        session.add(verb)
        session.commit()

        self.assertTrue(root.id is not None)
        self.assertTrue(p1.id is not None)
        self.assertTrue(p2.id is not None)
        self.assertTrue(verb.id is not None)
        session.close()

        # Root
        root = session.query(Root).first()
        vclasses = [x.id for x in root.vclasses]
        self.assertEqual(root.name, 'kf')
        self.assertEqual(vclasses, [enum['vclass']['5'], enum['vclass']['8']])

        # Verb
        verb = session.query(Verb).first()
        self.assertEqual(verb.name, 'karoti')
        self.assertEqual(verb.person_id, p)
        self.assertEqual(verb.number_id, n)
        self.assertEqual(verb.mode_id, m)
        self.assertEqual(verb.voice_id, v)

        # Root-verb associations
        self.assertEqual(root.id, verb.root_id)
        self.assertEqual(verb.root.name, 'kf')

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

        self.assertTrue(stem.id is not None)
        self.assertTrue(noun.id is not None)
        session.close()

        # Stem
        stem = session.query(Stem).first()
        self.assertEqual(stem.pos_id, Tag.NOUN)
        self.assertEqual(stem.name, 'nara')

        # Noun
        noun = session.query(Noun).first()
        self.assertEqual(noun.pos_id, Tag.NOUN)
        self.assertEqual(noun.name, 'narasya')
        self.assertEqual(noun.gender_id, enum['gender']['m'])
        self.assertEqual(noun.case_id, enum['case']['6'])
        self.assertEqual(noun.number_id, enum['number']['s'])

        # Stem-noun associtaions
        self.assertEqual(stem.id, noun.stem_id)

    def test_indeclinable(self):
        """Test indeclinables."""
        session = self.session

        ind = Indeclinable(name='ca')
        session.add(ind)
        session.commit()
        session.close()

        ind = session.query(Indeclinable).first()
        self.assertTrue(ind.id is not None)
        self.assertEqual(ind.pos_id, Tag.INDECLINABLE)
        self.assertEqual(ind.name, 'ca')

    def test_infinitive(self):
        """Test infinitives."""
        session = self.session

        root = self.add_root('gam')
        inf = Infinitive(name='gantum', root_id=root.id)
        session.add(inf)
        session.commit()
        session.close()

        inf = session.query(Infinitive).first()
        self.assertTrue(inf.id is not None)
        self.assertEqual(inf.pos_id, Tag.INFINITIVE)
        self.assertEqual(inf.name, 'gantum')
        self.assertEqual(inf.root.name, 'gam')

    def test_participle(self):
        """Test participles."""
        session = self.session
        enum = self.enum

        g, c, n = (enum['gender']['m'], enum['case']['2'], enum['number']['s'])

        root = self.add_root('car')
        part_stem = ParticipleStem(name='carat', root_id=root.id,
                                   mode_id=enum['mode']['pres'],
                                   voice_id=enum['voice']['P'])
        session.add(part_stem)
        session.flush()

        part = Participle(stem=part_stem, name='carantam', gender_id=g,
                          case_id=c, number_id=n)
        session.add(part)
        session.commit()
        session.close()

        part = session.query(Participle).first()
        self.assertTrue(part.id is not None)
        self.assertEqual(part.name, 'carantam')
        self.assertEqual(part.root.name, 'car')
        self.assertEqual(part.stem.name, 'carat')
        self.assertEqual(part.gender_id, g)
        self.assertEqual(part.case_id, c)
        self.assertEqual(part.number_id, n)

    def test_prefixed_verb(self):
        """Test prefixed verbs."""
        session = self.session
        enum = self.enum

        p, n, m, v = (enum['person']['3'], enum['number']['s'],
                      enum['mode']['pres'], enum['voice']['P'])

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

        self.assertTrue(root.id is not None)
        self.assertTrue(proot.id is not None)
        self.assertTrue(p1.id is not None)
        self.assertTrue(p2.id is not None)
        self.assertTrue(verb.id is not None)
        session.close()

        verb = session.query(Verb).first()
        prefixes = [x.name for x in verb.root.prefixes]
        self.assertEqual(verb.root.name, 'upasaMgam')
        self.assertEqual(prefixes, ['upa', 'sam'])

    def test_modified_verb(self):
        """Test modified verbs."""
        session = self.session
        enum = self.enum

        mod = enum['modification']['caus']
        p, n, m, v = (enum['person']['3'], enum['number']['s'],
                     enum['mode']['impv'], enum['voice']['P'])

        root = self.add_root('gam')
        mroot = ModifiedRoot(name='gamaya', basis_id=root.id)
        mroot.modifications = [session.query(Modification).get(mod)]
        session.add(mroot)
        session.flush()

        verb = Verb(name='gamayatu', root_id=mroot.id,
                person_id=p, number_id=n, mode_id=m, voice_id=v)
        session.add(verb)
        session.commit()

        self.assertTrue(root.id is not None)
        self.assertTrue(mroot.id is not None)
        self.assertTrue(verb.id is not None)
        session.close()

        verb = session.query(Verb).first()
        mods = [x.id for x in verb.root.modifications]
        self.assertEqual(verb.root.name, 'gamaya')
        self.assertEqual(verb.root.basis.name, 'gam')
        self.assertEqual(mods, [mod])

    def test_prefixed_modified_verb(self):
        """Test modified verbs with prefixes."""
        session = self.session
        enum = self.enum

        mod = enum['modification']['caus']
        p, n, m, v = (enum['person']['3'], enum['number']['s'],
                      enum['mode']['opt'], enum['voice']['P'])

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

        self.assertTrue(root.id is not None)
        self.assertTrue(pmroot.id is not None)
        self.assertTrue(verb.id is not None)
        session.close()
        verb = session.query(Verb).first()
        mods = [x.id for x in verb.root.modifications]
        prefixes = [x.name for x in verb.root.prefixes]
        self.assertEqual(verb.root.name, 'upasaMgamaya')
        self.assertEqual(verb.root.basis.name, 'gam')
        self.assertEqual(mods, [mod])
        self.assertEqual(prefixes, ['upa', 'sam'])
