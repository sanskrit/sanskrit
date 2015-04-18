# -*- coding: utf-8 -*-
"""
    sanskrit.schema
    ~~~~~~~~~~~~~~~

    Schema for Sanskrit data.
"""

import re

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.orm import relationship


Base = declarative_base()


class SimpleBase(Base):

    """A simple default base class.

    This automatically creates:

    - __tablename__
    - id (primary key)
    - name (string)
    """

    __abstract__ = True

    @declared_attr
    def __tablename__(cls):
        return re.sub('(?<!^)(?=[A-Z])', '_', cls.__name__).lower()

    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)

    def __repr__(self):
        cls = self.__class__.__name__
        return "%s%r" % (cls, (self.id, self.name))


class EnumBase(SimpleBase):

    """Base class for enumerations.

    Each enumeration has a name and an abbreviation.
    """

    __abstract__ = True
    abbr = Column(String)

    def __repr__(self):
        cls = self.__class__.__name__
        return "%s%r" % (cls, (self.id, self.name, self.abbr))


# Enumerations
# ------------
# Instead of enums, we use the following:

class Person(EnumBase):

    """Grammatical person:

    - first person, corresponding to Panini's **uttamapuruṣa**
    - second person, corresponding to Panini's **madhyamapuruṣa**
    - third person, corresponding to Panini's **prathamapuruṣa**
    """


class Number(EnumBase):

    """Grammatical number:

    - singular, corresponding to Panini's **ekavacana**
    - dual, corresponding to Panini's **dvivacana**
    - plural, corresponding to Panini's **bahuvacana**
    """


class Mode(EnumBase):

    """Tenses and moods:

    - present, corresponding to Panini's **laṭ**
    - aorist, corresponding to Panini's **luṅ**
    - imperfect, corresponding to Panini's **laṅ**
    - perfect, corresponding to Panini's **liṭ**
    - simple future, corresponding to Panini's **lṛṭ**
    - distant future, corresponding to Panini's **luṭ**
    - conditional, corresponding to Panini's **lṛṅ**
    - optative, corresponding to Panini's **vidhi-liṅ**
    - imperative, corresponding to Panini's **loṭ**
    - benedictive, corresponding to Panini's **āśīr-liṅ**
    - injunctive
    - future optative
    - future imperative
    """


class Voice(EnumBase):

    """Grammatical voice:

    - parasmaipada
    - ātmanepada
    - ubhayapada
    """


class Gender(EnumBase):

    """Grammatical gender:

    - masculine, corresponding to Panini's **puṃliṅga**
    - feminine, corresponding to Panini's **strīliṅga**
    - neuter, corresponding to Panini's **napuṃsakaliṅga**
    - unknown/undefined
    """


class GenderGroup(EnumBase):

    """Grammatical gender of a nominal stem. Since stems support nearly
    every combination of genders, this class stores both individual
    genders:

    - masculine
    - feminine
    - neuter
    - unknown/undefined

    and collections of genders:

    - masculine and feminine
    - masculine and neuter
    - feminine and neuter
    - masculine, feminine, and neuter
    """

    assocs = relationship('GenderGroupAssociation')
    members = association_proxy('assocs', 'gender')


class Case(EnumBase):

    """Grammatical case.

    - Nominative case, corresponding to Panini's **prathamā**
    - Accusative case, corresponding to Panini's **dvitīyā**
    - Instrumental case, corresponding to Panini's **tṛtīyā**
    - Dative case, corresponding to Panini's **caturthī**
    - Ablative case, corresponding to Panini's **pañcamī**
    - Genitive case, corresponding to Panini's **ṣaṣṭhī**
    - Locative case, corresponding to Panini's **saptamī**
    - Vocative case, corresponding to Panini's **saṃbodhana**
    """


class VClass(EnumBase):

    """Verb class:

    - class 1, corresponding to Panini's **bhvādi**
    - class 2, corresponding to Panini's **adādi**
    - class 3, corresponding to Panini's **juhotyādi**
    - class 4, corresponding to Panini's **divādi**
    - class 5, corresponding to Panini's **svādi**
    - class 6, corresponding to Panini's **tudādi**
    - class 7, corresponding to Panini's **rudhādi**
    - class 8, corresponding to Panini's **tanādi**
    - class 9, corresponding to Panini's **kryādi**
    - class 10, corresponding to Panini's **curādi**
    - class unknown, for verbs like "ah"
    - nominal, corresponding to various Paninian terms
    """

    __tablename__ = 'vclass'


class Modification(EnumBase):

    """Verb modification:

    - Causative, corresponding to Panini's **ṇic**
    - Desiderative, corresponding to Panini's **san**
    - Intensive, corresponding to Panini's **yaṅ**
    """


# Roots, stems, and forms
# =======================

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
    NOMINAL = 2
    PRONOUN = 3
    PARTICIPLE = 4
    INDECLINABLE = 5
    VERBAL_INDECLINABLE = 6
    GERUND = 7
    INFINITIVE = 8
    PERFECT_INDECLINABLE = 9
    NOUN_PREFIX = 10
    VERB_PREFIX = 11


# Unfinished forms
# ----------------
# Roots, stems, and prefixes

class Prefix(SimpleBase):

    """A generic prefix."""

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


class NominalEnding(SimpleBase):

    """A suffix for regular nouns and adjectives. This corresponds to
    Panini's **sup**."""

    CONSONANT_STEM_TYPE = '$cons'

    stem_type = Column(String)
    gender_id = Column(ForeignKey(Gender.id))
    case_id = Column(ForeignKey(Case.id))
    number_id = Column(ForeignKey(Number.id))
    compounded = Column(Boolean)

    gender = relationship(Gender)
    case = relationship(Case)
    number = relationship(Number)


class VerbEnding(SimpleBase):

    """A suffix for conjugated verbs of any kind. This corresponds to
    Panini's **tiṅ**."""

    #: Name of the stem category that uses this ending. This is useful
    #: for partitioning the list of endings according to the stem under
    #: consideration.
    #:
    #: The names of these groups depend on the initial data. The default
    #: data uses these names:
    #: - `'simple'` for classes 1, 4, 6, and 10
    #: - `'complex'` for classes 2, 3, 45, 7, 8, and 9
    #: - `'both'` for all classes
    category = Column(String)
    person_id = Column(ForeignKey(Person.id))
    number_id = Column(ForeignKey(Number.id))
    mode_id = Column(ForeignKey(Mode.id))
    voice_id = Column(ForeignKey(Voice.id))

    person = relationship(Person)
    number = relationship(Number)
    mode = relationship(Number)
    voice = relationship(Voice)


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

        | 1.4.13 Anything to which a suffix can be added is called an `aṅga`.

    But although "aṅga" also includes "dhātu," :class:`Stem` does
    not. Verb roots are stored in :class:`Root`.
    """

    genders_id = Column(ForeignKey(GenderGroup.id))
    pos_id = Column(ForeignKey(Tag.id))

    #: ``True`` iff a stem can produce its own words. For stems like "nara"
    #: or "agni" this value is ``True``. For stems like "ja" (dependent on
    #: upapada, as in "agra-ja") or "tva" (a suffix, as in "sama-tva"),
    #: this value is ``False``.
    dependent = Column(Boolean, default=False)

    genders = relationship(GenderGroup)
    pos = relationship(Tag)
    __mapper_args__ = {'polymorphic_on': pos_id}


class NominalStem(Stem):

    """Stem of a :class:`Nominal`."""

    __tablename__ = None
    __mapper_args__ = {'polymorphic_identity': Tag.NOMINAL}


class PronounStem(Stem):

    """Stem of a :class:`Pronoun`."""

    __tablename__ = None
    __mapper_args__ = {'polymorphic_identity': Tag.PRONOUN}


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


class StemIrregularity(Base):

    """Record of an irregular stem.

    Some Sanskrit stems are inflected irregularly. Since only an
    exceedingly small number of stems is irregular (< 100), it's
    easiest to record those irregularities in their own scheme.
    """

    __tablename__ = 'stem_irregularity'

    id = Column(ForeignKey(Stem.id), primary_key=True)

    #: If ``True``, assume that only the forms stored in the database
    #: are valid. If ``False``, assume that all unspecified forms can
    #: be generated by applying normal rules and endings to the stem.
    fully_described = Column(Boolean)

    stem = relationship(Stem)


# Completed forms
# ---------------
# Nouns, verbs, indeclinables, adjectives, and the like. In Paninian terms,
# these are all `pada`s.

class Form(SimpleBase):

    """A complete form. This corresponds to Panini's **pada**:

        | 1.4.14 Terms ending in "sup" and "tiṅ" are called `pada`.

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


class AbstractNominal(Form):

    """A complete nominal form. This corresponds to Panini's **subanta**."""

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


class Nominal(AbstractNominal):

    __tablename__ = None
    __mapper_args__ = {'polymorphic_identity': Tag.NOMINAL}


class Participle(AbstractNominal):

    """A complete form. This corresponds to Panini's **niṣṭhā** and **sat**.
    Moreover, it also corresponds to **kvasu**."""

    __tablename__ = None
    __mapper_args__ = {'polymorphic_identity': Tag.PARTICIPLE}

    root = association_proxy('stem', 'root')


# Associations
# ------------
# Code for building various many-to-many relationships

class GenderGroupAssociation(Base):

    __tablename__ = 'gender_group_assocs'

    id = Column(Integer, primary_key=True)
    group_id = Column(ForeignKey(GenderGroup.id))
    gender_id = Column(ForeignKey(Gender.id))

    group = relationship(GenderGroup)
    gender = relationship(Gender)

    def __init__(self, gender_id):
        self.gender_id = gender_id


class Paradigm(SimpleBase):

    """Represents an inflectional paradigm. This associates a root with a
    particular class and voice.
    """

    root_id = Column(ForeignKey(Root.id), index=True)
    vclass_id = Column(ForeignKey(VClass.id))
    voice_id = Column(ForeignKey(Voice.id))
    default = Column(Boolean, default=False)

    root = relationship(Root)
    vclass = relationship(VClass)
    voice = relationship(Voice)


class RootPrefixAssociation(SimpleBase):

    """Associates a prefixed root with a list of prefixes."""

    root_id = Column(ForeignKey(PrefixedRoot.id))
    prefix_id = Column(ForeignKey(VerbPrefix.id))
    position = Column(Integer)

    prefix = relationship(VerbPrefix)

    def __init__(self, prefix):
        self.prefix = prefix


class RootModAssociation(SimpleBase):

    """Associates a modified root with a list of modifications."""

    root_id = Column(ForeignKey(ModifiedRoot.id))
    modification_id = Column(ForeignKey(Modification.id))
    position = Column(Integer)

    modification = relationship(Modification)

    def __init__(self, modification):
        self.modification = modification


# Sandhi rules
# ============

class SandhiType(EnumBase):

    """Rule type. Sandhi rules are usually of three types:

    - *external* rules, which act between words
    - *internal* rules, which act between morphemes
    - *general* rules, which act in any context
    """


class SandhiRule(SimpleBase):

    __tablename__ = 'sandhi'

    first = Column(String)
    second = Column(String)
    result = Column(String)
    rule_type = Column(ForeignKey(SandhiType.id))

    def __repr__(self):
        values = (self.id, self.first, self.second, self.result)
        return 'SandhiRule(%r, %r, %r, %r)' % values
