"""
sanskrit.db.setup
~~~~~~~~~~~~~~~~~

Setup code for various Sanskrit data.
"""

import yaml
import xml.etree.ElementTree as ET
from sanskrit.schema import *

NOMINAL_MAPPER = {
    'm': Gender.MASCULINE,
    'f': Gender.FEMININE,
    'n': Gender.NEUTER,
    'mf': Gender.MF,
    'fn': Gender.FN,
    'mn': Gender.MN,
    'mfn': Gender.MFN,
    None: Gender.UNDEFINED,
    '1': Case.NOMINATIVE,
    '2': Case.ACCUSATIVE,
    '3': Case.INSTRUMENTAL,
    '4': Case.DATIVE,
    '5': Case.ABLATIVE,
    '6': Case.GENITIVE,
    '7': Case.LOCATIVE,
    '8': Case.VOCATIVE,
    's': Number.SINGULAR,
    'd': Number.DUAL,
    'p': Number.PLURAL
    }

def heading(s):
    """Print `s` as a heading."""
    print s
    print '-' * len(s)

def log(s):
    """Print `s` as a list item."""
    print ' -', s

def add_enums(session, ctx):
    """Add enumerated data to the database. Among others, this includes:

    - persons
    - numbers
    - modes
    - voices
    - genders
    - cases

    and any other data with small, known limits.
    """
    for cls in [Tag, Modification, VClass, Person, Number, Mode, Voice,
                Gender, Case, SandhiType]:
        log(cls.__name__)
        for key in dir(cls):
            if key.isupper():
                id = getattr(cls, key)
                session.add(cls(id=id, name=key.lower()))

    session.commit()
    session.close()

def add_sandhi(session, ctx):
    """Add sandhi rules to the database."""
    mapper = {
        'general': SandhiType.GENERAL,
        'internal': SandhiType.INTERNAL,
        'external': SandhiType.EXTERNAL
        }

    with open(ctx.config['SANDHI_DATA']) as f:
        for ruleset in yaml.load_all(f):
            rule_type = ruleset['type']
            log(rule_type)
            for rule in ruleset['rules']:
                rule['rule_type'] = mapper[rule_type]
                s = SandhiRule(**rule)
                session.add(s)

    session.commit()
    session.close()

def add_verb_prefixes(session, ctx):
    """Add verb prefixes to the database."""
    with open(ctx.config['VERB_PREFIX_DATA']) as f:
        for group in yaml.load_all(f):
            log(group['name'])
            for item in group['items']:
                prefix = VerbPrefix(name=item)
                session.add(prefix)
        session.commit()
    session.close()

def add_pronouns(session, ctx):
    """Add pronouns to the database."""
    mapper = NOMINAL_MAPPER
    with open(ctx.config['PRONOUN_DATA']) as f:
        for pronoun in yaml.load_all(f):
            gender_id = mapper[pronoun['genders']]
            stem = PronounStem(name=pronoun['stem'], gender_id=gender_id)
            session.add(stem)
            session.flush()
            log(stem.name)

            for item in pronoun['forms']:
                name = item['name']
                gender_id = mapper[item['gender']]
                case_id = mapper[item['case']]
                number_id = mapper[item['number']]
                result = Pronoun(stem=stem, name=name, gender_id=gender_id,
                                 case_id=case_id, number_id=number_id)
                session.add(result)
                session.flush()
        session.commit()
    session.close()

def create_tables(ctx):
    """Create tables in the database."""
    Base.metadata.create_all(ctx.engine)

def run(ctx):
    """Create and populate tables in the database."""
    session = ctx.session_class()
    create_tables(ctx)

    functions = [
        ('Enumerated data', add_enums),
        ('Sandhi rules', add_sandhi),
        ('Verb prefixes', add_verb_prefixes),
        ('Pronouns', add_pronouns),
        ]

    for name, f in functions:
        heading(name)
        f(session, ctx)
        print
