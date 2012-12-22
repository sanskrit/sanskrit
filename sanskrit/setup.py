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


def _add_verb_endings(session, ctx):
    """Add verb endings to the database."""
    with open(ctx.config['VERB_ENDING_DATA']) as f:
        person = ENUM['person']
        number = ENUM['number']
        mode = ENUM['mode']
        voice = ENUM['voice']

        for group in yaml.load_all(f):
            mode_id = mode[group['mode']]
            voice_id = voice[group['voice']]
            category = group['category']

            for row in group['endings']:
                kw = {
                    'name': row['name'],
                    'category': category,
                    'person_id': person[row['person']],
                    'number_id': number[row['number']],
                    'mode_id': mode_id,
                    'voice_id': voice_id,
                    }
                ending = VerbEnding(**kw)
                session.add(ending)
                session.flush()
            util.tick((group['mode'], group['voice'], category))

    session.commit()


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

    util.heading('Verb prefixes')
    prefixes = _add_verb_prefixes(session, ctx)

    util.heading('Verb endings')
    _add_verb_endings(session, ctx)

    util.heading('Roots and paradigms')
    roots = _add_roots(session, ctx)

    util.heading('Verbs')
    _add_verbs(session, ctx, roots)

    return

    util.heading('Prefixed roots')
    _add_prefixed_roots(session, ctx, root_map=roots, prefix_map=prefixes)


# Nominal data
# ------------
def _add_nominal_endings(session, ctx):
    with open(ctx.config['NOMINAL_ENDING_DATA']) as f:
        gender = ENUM['gender']
        case = ENUM['case']
        number = ENUM['number']

        for group in yaml.load_all(f):
            stem_type = group['stem']
            for row in group['endings']:
                kw = {
                    'name': row['name'],
                    'stem_type': stem_type,
                    'gender_id': gender[row['gender']],
                    'case_id': case.get(row.get('case')),
                    'number_id': number.get(row.get('number')),
                    'compounded': row.get('compounded', False)
                    }
                ending = NominalEnding(**kw)
                session.add(ending)
                session.flush()
            util.tick(stem_type)

    session.commit()


def _add_irregular_nouns(session, ctx):
    """Add irregular nouns to the database."""

    gender = ENUM['gender']
    case = ENUM['case']
    number = ENUM['number']

    with open(ctx.config['IRREGULAR_NOUN_DATA']) as f:
        for noun in yaml.load_all(f):
            gender_id = gender[noun['genders']]
            stem = NounStem(name=noun['stem'], gender_id=gender_id)
            session.add(stem)
            session.flush()

            # Mark the stem as irregular
            complete = noun['complete']
            irreg = StemIrregularity(stem=stem, fully_described=complete)
            session.add(irreg)
            session.flush()

            util.tick(stem.name)

            for form in noun['forms']:
                name = form['name']
                gender_id = gender[form['gender']]
                case_id = case[form['case']]
                number_id = number[form['number']]

                result = Noun(stem=stem, name=name, gender_id=gender_id,
                              case_id=case_id, number_id=number_id)
                session.add(result)
                session.flush()

    session.commit()


def _add_regular_nouns(session, ctx):
    """Add regular nouns to the database."""

    conn = ctx.engine.connect()
    ins = NounStem.__table__.insert()
    gender = ENUM['gender']
    pos_id = Tag.NOUN

    buf = []
    i = 0
    with open(ctx.config['NOUN_DATA']) as f:
        for noun in yaml.load_all(f):
            name = noun['name']
            gender_id = gender[noun['genders']]
            buf.append({
                'name': name,
                'pos_id': pos_id,
                'gender_id': gender_id,
                })

            i += 1
            if i % 500 == 0:
                util.tick(name)
                conn.execute(ins, buf)
                buf = []

    if buf:
        conn.execute(ins, buf)


def add_nominals(session, ctx):
    util.heading('Nominal endings')
    _add_nominal_endings(session, ctx)

    util.heading('Irregular nouns')
    _add_irregular_nouns(session, ctx)

    util.heading('Regular nouns')
    _add_regular_nouns(session, ctx)


# Pronominal forms
# ----------------

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
    session = ctx.session

    functions = [
        ('Tags', add_tags),
        ('Enumerated data', add_enums),
        ('Nominal data', add_nominals),
        ('Sandhi rules', add_sandhi),
        ('Indeclinables', add_indeclinables),
        ('Verbal data', add_verbal),
        ('Pronoun data', add_pronouns),
        ]

    for name, f in functions:
        util.heading(name, '=')
        f(session, ctx)
