"""
sanskrit.db.setup
~~~~~~~~~~~~~~~~~

Setup code for various Sanskrit data.
"""

import yaml

from sanskrit import util
from sanskrit.schema import *

# Populated in `add_enums`
ENUM = {}


# Miscellaneous
# -------------

def add_tags(session, ctx):
    for key in dir(Tag):
        if key.isupper():
            id = getattr(Tag, key)
            session.add(Tag(id=id, name=key.lower()))


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

    classes = [Modification, VClass, Person, Number, Mode, Voice,
               Gender, Case, SandhiType]
    names = [c.__name__ for c in classes]
    mapper = dict(zip(names, classes))

    with open(ctx.config['ENUM_DATA']) as f:
        for enum in yaml.load(f):
            enum_name = enum['name']
            cls = mapper[enum_name]
            enum_abbr = cls.__tablename__
            ENUM[enum_abbr] = {}

            for item in enum['items']:
                item_name = item['name']
                abbr = item['abbr']
                e = cls(name=item_name, abbr=abbr)

                session.add(e)
                session.flush()
                ENUM[enum_abbr][abbr] = e.id

            util.tick(cls.__name__)

    session.commit()
    session.close()


def add_sandhi(session, ctx):
    """Add sandhi rules to the database."""
    stype = ENUM['sandhi_type']

    with open(ctx.config['SANDHI_DATA']) as f:
        for ruleset in yaml.load_all(f):
            rule_type = ruleset['type']
            util.tick(rule_type)
            for rule in ruleset['rules']:
                rule['rule_type'] = stype[rule_type]
                s = SandhiRule(**rule)
                session.add(s)

    session.commit()
    session.close()


def add_indeclinables(session, ctx):
    """Add indeclinables to the database."""
    with open(ctx.config['INDECLINABLE_DATA']) as f:
        for i, name in enumerate(yaml.load(f)):
            ind = Indeclinable(name=name)
            session.add(ind)
            if i % 200 == 0:
                util.tick(name)

    session.commit()
    session.close()


# Verbal forms
# ------------

def _add_verb_prefixes(session, ctx):
    """Add verb prefixes to the database."""
    prefix_map = {}
    with open(ctx.config['VERB_PREFIX_DATA']) as f:
        for group in yaml.load_all(f):
            util.tick(group['name'])
            for name in group['items']:
                prefix = VerbPrefix(name=name)
                session.add(prefix)
                session.flush()
                prefix_map[name] = prefix.id

    session.commit()
    session.close()
    return prefix_map


def _add_roots(session, ctx):
    """Add verb roots to the database."""

    vclass = ENUM['vclass']
    voice = ENUM['voice']

    root_map = {}  # (name, hom) -> id
    with open(ctx.config['ROOT_DATA']) as f:
        for i, item in enumerate(yaml.load_all(f)):
            name = item['name']
            paradigms = item['paradigms']

            root = Root(name=name)
            session.add(root)
            session.flush()

            for row in paradigms:
                paradigm = Paradigm(root_id=root.id,
                                    vclass_id=vclass[row[0]],
                                    voice_id=voice[row[1]])
                session.add(paradigm)

            hom = item.get('hom', None)
            root_map[(name, hom)] = root.id

            if i % 100 == 0:
                util.tick(name)

    session.commit()
    session.close()
    return root_map


def _add_prefixed_roots(session, ctx, root_map=None, prefix_map=None):
    """Add prefixed roots to the database."""

    homs = [None] + [str(i) for i in range(1, 10)]

    # Contains roots that weren't added by `add_roots`.
    missed = set()

    with open(ctx.config['PREFIXED_ROOT_DATA']) as f:
        for i, item in enumerate(yaml.load_all(f)):
            name = item['name']
            basis = item['basis']
            hom = item.get('hom', None)
            prefixes = item['prefixes']

            basis_id = None
            try:
                basis_id = root_map[(basis, hom)]
            except KeyError:
                for hom in homs:
                    try:
                        basis_id = root_map[(basis, hom)]
                    except KeyError:
                        pass

            if basis_id is None:
                candidates = [k for k in root_map.keys() if k[0] == basis]
                print 'SKIPPED:', name, basis, candidates
                missed.add(basis)
                continue

            prefixed_root = PrefixedRoot(name=name, basis_id=basis_id)
            session.add(prefixed_root)
            session.flush()

            for prefix in prefixes:
                pass

            if i % 100 == 0:
                util.tick(name)

    session.commit()
    session.close()
    print missed


def _add_modified_roots(session, ctx):
    """Add modified roots to the database."""


def _add_verbs(session, ctx, root_map=None):
    """Add inflected verbs to the database."""

    vclass = ENUM['vclass']
    person = ENUM['person']
    number = ENUM['number']
    mode = ENUM['mode']
    voice = ENUM['voice']
    i = 0

    with open(ctx.config['VERB_DATA']) as f:
        for item in yaml.load_all(f):
            root = item['name']
            hom = item['hom']

            try:
                root_id = root_map[(root, hom)]
            except KeyError:
                print 'SKIPPED:', root, hom
                continue

            for row in item['forms']:
                form = {
                    'name': row['name'],
                    'root_id': root_id,
                    'vclass_id': vclass[row['vclass']],
                    'person_id': person[row['person']],
                    'number_id': number[row['number']],
                    'mode_id': mode[row['mode']],
                    'voice_id': voice[row['voice']]
                }
                session.add(Verb(**form))
                i += 1

            if i % 100 == 0:
                util.tick(root)

    session.commit()
    session.close()


def add_verbal(session, ctx):
    """Add all verb data to the database, including:

    - roots
    - prefixed roots
    - modified roots
    - prefixed modified roots
    - inflected verbs
    - gerunds
    - infinitives
    """

    util.heading('Roots and paradigms')
    roots = _add_roots(session, ctx)

    util.heading('Verbs')
    _add_verbs(session, ctx, roots)

    return

    util.heading('Verb prefixes')
    prefixes = _add_verb_prefixes(session, ctx)

    util.heading('Prefixed roots')
    _add_prefixed_roots(session, ctx, root_map=roots, prefix_map=prefixes)


def add_pronouns(session, ctx):
    """Add pronouns to the database."""

    gender = ENUM['gender']
    case = ENUM['case']
    number = ENUM['number']

    with open(ctx.config['PRONOUN_DATA']) as f:
        for pronoun in yaml.load_all(f):
            gender_id = gender[pronoun['genders']]
            stem = PronounStem(name=pronoun['stem'], gender_id=gender_id)
            session.add(stem)
            session.flush()
            util.tick(stem.name)

            for item in pronoun['forms']:
                name = item['name']
                gender_id = gender[item['gender']]
                case_id = case[item['case']]
                number_id = number[item['number']]

                result = Pronoun(stem=stem, name=name, gender_id=gender_id,
                                 case_id=case_id, number_id=number_id)
                session.add(result)
                session.flush()
        session.commit()
    session.close()


def run(ctx):
    """Create and populate tables in the database."""
    ctx.drop_all()
    ctx.create_all()
    session = ctx.session_class()

    functions = [
        ('Tags', add_tags),
        ('Enumerated data', add_enums),
        ('Sandhi rules', add_sandhi),
        ('Indeclinables', add_indeclinables),
        ('Verbal data', add_verbal),
        ('Pronouns', add_pronouns),
        ]

    for name, f in functions:
        util.heading(name, '=')
        f(session, ctx)
