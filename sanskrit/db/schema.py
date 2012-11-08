# -*- coding: utf-8 -*-
"""
sanskrit.db.schema
~~~~~~~~~~~~~~~~~~

Schema for all Sanskrit data.
"""

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.orm import relationship

# Base classes
# ------------
Base = declarative_base()

class SimpleBase(Base):

    """A simple default base class. This automatically creates a table name,
    a primary key, and a `name` field for some payload.
    """

    __abstract__ = True

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True)
    name = Column(String)


# Enumerations
# ------------
# Instead of enums, we use the following:

class Tag(SimpleBase):

    """Part of speech tag. It contains the following:

    - noun
    - pronoun
    - adjective
    - indeclinable
    - verb
    - gerund
    - infinitive
    - participle
    - perfect indeclinable (also known as the *periphrastic perfect*)
    - noun prefix
    - verb prefix
    """

    VERB = 1
    NOUN = 2
    PRONOUN = 3
    ADJECTIVE = 4
    PARTICIPLE = 5
    INDECLINABLE = 6
    VERBAL_INDECLINABLE = 7
    GERUND = 8
    INFINITIVE = 9
    PERFECT_INDECLINABLE = 10
    NOUN_PREFIX = 11
    VERB_PREFIX = 12


class Person(SimpleBase):

    """Grammatical person."""

    #: First person, corresponding to Panini's **uttamapuruṣa**.
    FIRST = 1
    #: Second person, corresponding to Panini's **madhyamapuruṣa**.
    SECOND = 2
    #: Third person, corresponding to Panini's **prathamapuruṣa**.
    THIRD = 3


class Number(SimpleBase):

    """Grammatical number."""

    #: Singular number, corresponding to Panini's **ekavacana**.
    SINGULAR = 1
    #: Dual number, corresponding to Panini's **dvivacana**.
    DUAL = 2
    #: Plural number, corresponding to Panini's **bahuvacana**.
    PLURAL = 3


class Mode(SimpleBase):

    """Verb mode. In addition to representing the basic tenses and moods
    described in the Ashtadhyayi, :class:`Mode` also contains composite
    modes like "future optative" and "future imperative."
    """

    #: Present, corresponding to Panini's **laṭ**.
    PRESENT = 1
    #: Aorist, corresponding to Panini's **luṅ**.
    AORIST = 2
    #: Imperfect, corresponding to Panini's **laṅ**.
    IMPERFECT = 3
    #: Perfect, corresponding to Panini's **liṭ**.
    PERFECT = 4
    #: Simple future, corresponding to Panini's **lṛṭ**.
    SIMPLE_FUTURE = 5
    #: Distant future, corresponding to Panini's **luṭ**.
    DISTANT_FUTURE = 6
    #: Conditional, corresponding to Panini's **lṛṅ**.
    CONDITIONAL = 7
    #: Optative, corresponding to Panini's **liṅ**.
    OPTATIVE = 8
    #: Imperative, corresponding to Panini's **loṭ**.
    IMPERATIVE = 9
    #: Benedictive
    BENEDICTIVE = 10
    #: Injunctive
    INJUNCTIVE = 11
    #: Future optative
    FUTURE_OPTATIVE = 12
    #: Future imperative
    FUTURE_IMPERATIVE = 13


class Voice(SimpleBase):

    """Grammatical voice."""

    #: Parasmaipada
    PARASMAIPADA = 1
    #: Atmanepada
    ATMANEPADA = 2
    #: A combination of parasmaipada and atmanepada.
    UBHAYAPADA = 3


class Gender(SimpleBase):

    """Grammatical gender. This class is overloaded to handle two kinds of
    gender:

    - :class:`Nominal` gender, which is masculine, feminine, neuter, or other
    - :class:`Stem` gender, which can also be any combination of masculine,
      feminine, and neuter
    """

    #: Masculine gender, corresponding to Panini's **puṃliṅga**.
    MASCULINE = 1
    #: Feminine gender, corresponding to Panini's **strīliṅga**.
    FEMININE = 2
    #: Neuter gender, corresponding to Panini's **napuṃsakaliṅga**.
    NEUTER = 3
    #: Masculine or feminine gender
    MF = 4
    #: Feminine or neuter gender
    FN = 5
    #: Masculine or neuter gender
    MN = 6
    #: Any gender
    MFN = 7
    #: Unknown or undefined gender
    UNDEFINED = 8


class Case(SimpleBase):

    """Grammatical case."""

    #: Nominative case, corresponding to Panini's **prathamā**.
    NOMINATIVE = 1
    #: Accusative case, corresponding to Panini's **dvitīyā**.
    ACCUSATIVE = 2
    #: Instrumental case, corresponding to Panini's **tṛtīyā**.
    INSTRUMENTAL = 3
    #: Dative case, corresponding to Panini's **caturthī**.
    DATIVE = 4
    #: Ablative case, corresponding to Panini's **pañcamī**.
    ABLATIVE = 5
    #: Genitive case, corresponding to Panini's **ṣaṣṭhī**.
    GENITIVE = 6
    #: Locative case, corresponding to Panini's **saptamī**.
    LOCATIVE = 7
    #: Vocative case, corresponding to Panini's **saṃbodhana**.
    VOCATIVE = 8


class VClass(SimpleBase):

    """Verb class."""

    #: Class 1, corresponding to Panini's **bhvādi**.
    C1 = 1
    #: Class 2, corresponding to Panini's **adādi**.
    C2 = 2
    #: Class 3, corresponding to Panini's **juhotyādi**.
    C3 = 3
    #: Class 4, corresponding to Panini's **divādi**.
    C4 = 4
    #: Class 5, corresponding to Panini's **svādi**.
    C5 = 5
    #: Class 6, corresponding to Panini's **tudādi**.
    C6 = 6
    #: Class 7, corresponding to Panini's **rudhādi**.
    C7 = 7
    #: Class 8, corresponding to Panini's **tanādi**.
    C8 = 8
    #: Class 9, corresponding to Panini's **kryādi**.
    C9 = 9
    #: Class 10, corresponding to Panini's **curādi**.
    C10 = 10
    #: Denominative verbs, corresponding to varios Paninian terms.
    DENOMINATIVE = 11
    #: Class unknown, for verbs like "ah".
    UNKNOWN = 12


class Modification(SimpleBase):

    """Verb modification."""

    #: Causative, corresponding to Panini's **ṇic**.
    CAUSATIVE = 1
    #: Desiderative, corresponding to Panini's **san**.
    DESIDERATIVE = 2
    #: Intensive, corresponding to Panini's **yaṅ**.
    INTENSIVE = 3


# Unfinished forms
# ----------------
# Roots, stems, and prefixes

class Prefix(SimpleBase):

    """A generic prefix. This is a superclass of :class:`VerbPrefix` and
    :class:`NounPrefix`.
    """

    pos_id = Column(ForeignKey(Tag.id))

    pos = relationship(Tag)
    __mapper_args__ = {'polymorphic_on': pos_id}


class VerbPrefix(Prefix):

    """A verb prefix. This corresponds to Panini's **gati**, which includes
    **cvi** (`svāgatī-karoti`) and **upasarga** (`anu-karoti`).
    """

    __tablename__ = None
    __mapper_args__ = {'polymorphic_identity': Tag.VERB_PREFIX}


class NounPrefix(Prefix):

    """A noun prefix. This includes `nañ`, among others."""

    __tablename__ = None
    __mapper_args__ = {'polymorphic_identity': Tag.NOUN_PREFIX}


class Root(SimpleBase):

    """A verb root. This corresponds to Panini's **dhātu**:

        | 1.3.1 "bhū" etc. are called `dhātu`.
        | 3.1.22 Terms ending in `san` etc. are called dhātu.

    Moreover, :class:`Root` contains prefixed roots. Although this modeling
    choice is non-Paninian, it does express the notion that verb prefixes can
    cause profound changes in a root's meaning and identity.
    """

    # re-declared for use with `remote_side` below
    id = Column(Integer, primary_key=True)

    #: The ultimate ancestor of this root. For instance, the basis of
    #: "sam-upa-gam" is "gam".
    basis_id = Column(ForeignKey('root.id'))
    discriminator = Column(Integer)

    basis = relationship('Root', remote_side=[id])
    paradigms = relationship('Paradigm')
    vclasses = association_proxy('paradigms', 'vclass')
    voices = association_proxy('paradigms', 'voice')
    __mapper_args__ = {'polymorphic_on': discriminator}


class PrefixedRoot(Root):

    """A root with one or more prefixes."""

    __tablename__ = None
    __mapper_args__ = {'polymorphic_identity': 1}

    prefix_assocs = relationship('RootPrefixAssociation',
                                 collection_class=ordering_list('position'),
                                 order_by='RootPrefixAssociation.position')
    prefixes = association_proxy('prefix_assocs', 'prefix')


class ModifiedRoot(Root):

    """A root with one or more modifications."""

    __tablename__ = None
    __mapper_args__ = {'polymorphic_identity': 2}

    mod_assocs = relationship('RootModAssociation',
                              collection_class=ordering_list('position'),
                              order_by='RootModAssociation.position')
    modifications = association_proxy('mod_assocs', 'modification')


class PrefixedModifiedRoot(PrefixedRoot, ModifiedRoot):

    """A prefixed root with one or more modifications."""

    __mapper_args__ = {'polymorphic_identity': 3}

    # `mod_assocs` and `modifications` are not defined automatically, despite
    # the diamond inheritance for this class.
    mod_assocs = relationship('RootModAssociation',
                              collection_class=ordering_list('position'),
                              order_by='RootModAssociation.position')
    modifications = association_proxy('mod_assocs', 'modification')


class Stem(SimpleBase):

    """A nominal stem. This corresponds to Panini's **aṅga**:

        1.4.13 Anything to which a suffix can be added is called an `aṅga`.

    But although "aṅga" also includes "dhātu," :class:`Stem` does
    not. Verb roots are stored in :class:`Root`.
    """

    gender_id = Column(ForeignKey(Gender.id))
    pos_id = Column(ForeignKey(Tag.id))

    #: ``True`` iff a stem can produce its own words. For stems like "nara"
    #: or "agni" this value is ``True``. For stems like "ja" (dependent on
    #: upapada, as in "agra-ja") or "tva" (a suffix, as in "sama-tva"),
    #: this value is ``False``.
    dependent = Column(Boolean, default=False)

    gender = relationship(Tag)
    pos = relationship(Tag)
    __mapper_args__ = {'polymorphic_on': pos_id}


class NounStem(Stem):

    """Stem of a :class:`Noun`."""

    __tablename__ = None
    __mapper_args__ = {'polymorphic_identity': Tag.NOUN}


class PronounStem(Stem):

    """Stem of a :class:`Pronoun`."""

    __tablename__ = None
    __mapper_args__ = {'polymorphic_identity': Tag.PRONOUN}


class AdjectiveStem(Stem):

    """Stem of an :class:`Adjective`."""

    __tablename__ = None
    __mapper_args__ = {'polymorphic_identity': Tag.ADJECTIVE}


class ParticipleStem(Stem):

    """Stem of a :class:`Participle`."""

    __tablename__ = 'participlestem'
    __mapper_args__ = {'polymorphic_identity': Tag.PARTICIPLE}

    id = Column(ForeignKey(Stem.id), primary_key=True)

    root_id = Column(ForeignKey(Root.id))
    mode_id = Column(ForeignKey(Mode.id))
    voice_id = Column(ForeignKey(Voice.id))

    root = relationship(Root, backref='participle_stems')
    mode = relationship(Mode)
    voice = relationship(Voice)


# Completed forms
# ---------------
# Nouns, verbs, indeclinables, adjectives, and the like. In Paninian terms,
# these are all `pada`s.

class Form(SimpleBase):

    """A complete form. This corresponds to Panini's **pada**:

        1.4.14 Terms ending in "sup" and "tiṅ" are called `pada`.

    In other words, a :class:`Form` is a self-contained linguistic unit that
    could be used in a sentence as-is.
    """

    pos_id = Column(ForeignKey(Tag.id))

    pos = relationship(Tag)
    __mapper_args__ = {'polymorphic_on': pos_id}


class Indeclinable(Form):

    """A complete form. This corresponds to Panini's **avyaya**."""

    __tablename__ = None
    __mapper_args__ = {'polymorphic_identity': Tag.INDECLINABLE}


class Verb(Form):

    """A complete form. This corresponds to Panini's **tiṅanta**."""

    __tablename__ = 'verb'
    __mapper_args__ = {'polymorphic_identity': Tag.VERB}

    id = Column(ForeignKey(Form.id), primary_key=True)

    root_id = Column(ForeignKey(Root.id))
    vclass_id = Column(ForeignKey(VClass.id))
    person_id = Column(ForeignKey(Person.id))
    number_id = Column(ForeignKey(Number.id))
    mode_id = Column(ForeignKey(Mode.id))
    voice_id = Column(ForeignKey(Voice.id))

    root = relationship(Root, backref='verbs')
    person = relationship(Person)
    number = relationship(Number)
    mode = relationship(Mode)
    voice = relationship(Voice)


class VerbalIndeclinable(Form):

    """A complete form. :class:`VerbalIndeclinable` is a superclass for
    three more specific classes: :class:`Gerund`, :class:`Infinitive`, and
    :class:`PerfectIndeclinable`.
    """

    __tablename__ = 'verbalindeclinable'
    __mapper_args__ = {'polymorphic_identity': Tag.VERBAL_INDECLINABLE}

    id = Column(ForeignKey(Form.id), primary_key=True)
    root_id = Column(ForeignKey(Root.id))

    root = relationship(Root)


class Infinitive(VerbalIndeclinable):

    """A complete form. This corresponds to Panini's **tumanta**."""

    __tablename__ = None
    __mapper_args__ = {'polymorphic_identity': Tag.INFINITIVE}


class Gerund(VerbalIndeclinable):

    """A complete form. This corresponds to Panini's **ktvānta** and
    **lyabanta**."""

    __tablename__ = None
    __mapper_args__ = {'polymorphic_identity': Tag.GERUND}


class PerfectIndeclinable(VerbalIndeclinable):

    """A complete form. This corresponds to forms ending in the suffix **ām**,
    as in "īkṣāṃ cakre".
    """

    __tablename__ = None
    __mapper_args__ = {'polymorphic_identity': Tag.PERFECT_INDECLINABLE}


class Nominal(Form):

    """A complete form. This corresponds to Panini's **subanta**."""

    __tablename__ = 'nominal'
    id = Column(ForeignKey(Form.id), primary_key=True)
    stem_id = Column(ForeignKey(Stem.id))
    gender_id = Column(ForeignKey(Gender.id))
    case_id = Column(ForeignKey(Case.id))
    number_id = Column(ForeignKey(Number.id))
    compounded = Column(Boolean)

    stem = relationship(Stem, backref='forms')
    gender = relationship(Gender)
    case = relationship(Case)
    number = relationship(Number)


class Noun(Nominal):

    """A complete form."""

    __tablename__ = None
    __mapper_args__ = {'polymorphic_identity': Tag.NOUN}


class Pronoun(Nominal):

    """A complete form. This partially corresponds to Panini's **sarvanāman**:

        1.1.26 "sarva" etc. are called `sarvanāman`.

    However, adjectival words like "sarva" and "eka" are stored as adjectives.
    """

    __tablename__ = None
    __mapper_args__ = {'polymorphic_identity': Tag.PRONOUN}


class Adjective(Nominal):

    """A complete form. This corresponds to Panini's **viśeṣaṇa**."""

    __tablename__ = None
    __mapper_args__ = {'polymorphic_identity': Tag.ADJECTIVE}


class Participle(Nominal):

    """A complete form. This corresponds to Panini's **niṣṭhā** and **sat**.
    Moreover, it also corresponds to **kvasu**."""

    __tablename__ = None
    __mapper_args__ = {'polymorphic_identity': Tag.PARTICIPLE}

    root = association_proxy('stem', 'root')


# Associations
# ------------
# Code for building various many-to-many relationships

class Paradigm(Base):

    """Represents an inflectional paradigm. This associates a root with a
    particular class and voices.
    """

    __tablename__ = 'paradigm'

    id = Column(Integer, primary_key=True)
    root_id = Column(ForeignKey(Root.id), index=True)
    vclass_id = Column(ForeignKey(VClass.id))
    voice_id = Column(ForeignKey(Voice.id))
    default = Column(Boolean, default=False)

    root = relationship(Root)
    vclass = relationship(VClass)
    voice = relationship(Voice)


class RootPrefixAssociation(Base):

    """Associates a prefixed root with a list of prefixes."""

    __tablename__ = 'root_prefix_association'
    id = Column(Integer, primary_key=True)
    root_id = Column(ForeignKey(PrefixedRoot.id))
    prefix_id = Column(ForeignKey(VerbPrefix.id))
    position = Column(Integer)

    prefix = relationship(VerbPrefix)

    def __init__(self, prefix):
        self.prefix = prefix


class RootModAssociation(Base):

    """Associates a modified root with a list of modifications."""

    __tablename__ = 'root_mod_association'
    id = Column(Integer, primary_key=True)
    root_id = Column(ForeignKey(ModifiedRoot.id))
    modification_id = Column(ForeignKey(Modification.id))
    position = Column(Integer)

    modification = relationship(Modification)

    def __init__(self, modification):
        self.modification = modification
