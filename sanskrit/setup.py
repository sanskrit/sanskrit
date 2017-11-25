"""
sanskrit.setup
~~~~~~~~~~~~~~

Setup code for various Sanskrit data.
"""
from __future__ import print_function

import sys

from sanskrit import util
from sanskrit.schema import *

import sqlalchemy.schema

# Populated in `add_enums`
ENUM = {}


# Miscellaneous
# -------------

def add_tags(ctx):
    """Populate the `Tag` table."""
    session = ctx.session
    for key in dir(Tag):
        if key.isupper():
            id = getattr(Tag, key)
            session.add(Tag(id=id, name=key.lower()))
    session.commit()
    session.close()


def add_enums(ctx):
    """Add enumerated data to the database. Among others, this includes:

    - persons
    - numbers
    - modes
    - voices
    - genders
    - cases

    and any other data with small, known limits.
    """

    session = ctx.session
    type_to_class = {
        'case': Case,
        'class': VClass,
        'gender': Gender,
        'gender_group': GenderGroup,
        'modification': Modification,
        'mode': Mode,
        'number': Number,
        'person': Person,
        'sandhi_rule_type': SandhiType,
        'voice': Voice,
    }

    # First pass: ordinary enums
    for row in util.read_csv(ctx.config['ENUMS']):
        if row['enum_type'] == 'gender_group':
            continue

        cls = type_to_class.get(row['enum_type'], None)
        # TODO: always non-None?
        if cls is None:
            continue

        enum_abbr = cls.__tablename__
        if enum_abbr not in ENUM:
            util.tick(cls.__name__)
        ENUM.setdefault(enum_abbr, {})

        abbreviation = row['abbreviation']
        e = cls(name=row['human_readable_value'], abbr=abbreviation)
        session.add(e)
        session.flush()
        ENUM[enum_abbr][abbreviation] = e.id
    session.commit()

    # Second pass: gender groups
    for row in util.read_csv(ctx.config['ENUMS']):
        if row['enum_type'] != 'gender_group':
            continue

        cls = type_to_class.get(row['enum_type'], None)
        enum_abbr = cls.__tablename__
        if enum_abbr not in ENUM:
            util.tick(cls.__name__)
        ENUM.setdefault(enum_abbr, {})

        abbreviation = row['abbreviation']
        e = cls(name=row['human_readable_value'], abbr=abbreviation)
        session.add(e)
        session.flush()

        if set(abbreviation).issubset('mfn'):
            e.members = [ENUM['gender'][x] for x in abbreviation]

        ENUM[enum_abbr][abbreviation] = e.id

    session.commit()
    session.close()


def add_sandhi_rules(ctx):
    """Add sandhi rules to the database."""
    session = ctx.session
    stype = ENUM['sandhi_type']

    for row in util.read_csv(ctx.config['SANDHI_RULES']):
        session.add(SandhiRule(first=row['first'], second=row['second'],
                               result=row['result'],
                               rule_type=stype[row['type']]))
    session.commit()
    session.close()


def add_indeclinables(ctx):
    """Add indeclinables to the database."""
    session = ctx.session
    tick = util.tick_every(300)

    for row in util.read_csv(ctx.config['INDECLINABLES']):
        session.add(Indeclinable(name=row['name']))
        tick(row['name'])

    session.commit()
    session.close()


def add_verb_prefixes(ctx):
    """Add verb prefixes to the database."""
    session = ctx.session
    prefix_map = {}

    for row in util.read_csv(ctx.config['VERB_PREFIXES']):
        # TODO: use prefix type?
        prefix = VerbPrefix(name=row['name'])
        session.add(prefix)
        session.flush()
        prefix_map[row['name']] = prefix.id

    session.commit()
    session.close()
    return prefix_map


def add_verb_endings(ctx):
    """Add verb endings to the database."""
    session = ctx.session
    person = ENUM['person']
    number = ENUM['number']
    mode = ENUM['mode']
    voice = ENUM['voice']

    for row in util.read_csv(ctx.config['VERB_ENDINGS']):
        session.add(VerbEnding(name=row['ending'],
                               category=row['category'],
                               person_id=person[row['person']],
                               number_id=number[row['number']],
                               mode_id=mode[row['mode']],
                               voice_id=voice[row['voice']]))
    session.commit()
    session.close()


def add_roots(ctx, prefix_map):
    """Populates :class:`Root` and its subclasses."""

    # TODO: modified roots
    session = ctx.session
    e_vclass = ENUM['vclass']
    e_voice = ENUM['voice']

    root_map = {}  # (name, hom) -> id

    # First pass: Root
    tick = util.tick_every(100)
    for row in util.read_csv(ctx.config['UNPREFIXED_ROOTS']):
        name, hom = row['root'], row['hom']

        # A root can have multiple paradigms (= multiple appearances)
        if (name, hom) in root_map:
            continue

        root = Root(name=name)
        session.add(root)
        session.flush()
        root_map[(name, hom)] = root.id

        tick(name)

    # Second pass: Paradigm
    for row in util.read_csv(ctx.config['UNPREFIXED_ROOTS']):
        name, hom = row['root'], row['hom']
        vclass, voice = row['class'], row['voice']

        assert (name, hom) in root_map
        root_id = root_map[(name, hom)]
        paradigm = Paradigm(root_id=root_id, vclass_id=e_vclass[vclass],
                            voice_id=e_voice[voice])
        session.add(paradigm)

    session.commit()

    # Prefixed roots
    for i, row in enumerate(util.read_csv(ctx.config['PREFIXED_ROOTS'])):
        name = row['prefixed_root']
        basis = row['unprefixed_root']
        hom = row['hom']
        prefixes = row['prefixes'].split('-')

        assert (basis, hom) in root_map
        basis_id = root_map[(basis, hom)]
        for prefix in prefixes:
            # TODO
            pass

        prefixed_root = PrefixedRoot(name=name, basis_id=basis_id)
        session.add(prefixed_root)
        session.flush()
        root_map[(name, hom)] = prefixed_root.id

        tick(name)

    session.commit()
    session.close()

    return root_map


def add_verbs(ctx, root_map):
    """Add inflected verbs to the database."""

    session = ctx.session
    vclass = ENUM['vclass']
    person = ENUM['person']
    number = ENUM['number']
    mode = ENUM['mode']
    voice = ENUM['voice']
    skipped = set()
    i = 0

    for row in util.read_csv(ctx.config['VERBS']):
        root = row['root']
        hom = row['hom']

        try:
            root_id = root_map[(root, hom)]
        except KeyError:
            skipped.add((root, hom))
            continue

        data = {
            'name': row['form'],
            'root_id': root_id,
            'vclass_id': vclass[row['class']] if row['class'] else None,
            'person_id': person[row['person']],
            'number_id': number[row['number']],
            'mode_id': mode[row['mode']],
            'voice_id': voice[row['voice']]
        }
        session.add(Verb(**data))

        i += 1
        if i % 1000 == 0:
            util.tick(row['form'])
            session.commit()

    session.commit()
    session.close()
    print('Skipped', len(skipped), 'roots.')


def add_verbal_indeclinables(ctx, root_map):
    session = ctx.session
    root_map = root_map or {}
    skipped = set()

    for row in util.read_csv(ctx.config['VERBAL_INDECLINABLES']):
        root, hom, pos = row['root'], row['hom'], row['pos']

        try:
            root_id = root_map[(root, hom)]
        except KeyError:
            skipped.add((root, hom))
            continue

        # TODO: modifications!
        datum = {
            'name': row['form'],
            'root_id': root_id
        }
        if pos == 'gerund':
            session.add(Gerund(**datum))
        elif pos == 'infinitive':
            session.add(Infinitive(**datum))
        else:
            assert False

    session.commit()


def add_participle_stems(ctx, root_map):
    """Populates `ParticipleStem`."""

    session = ctx.session
    root_map = root_map or {}
    mode = ENUM['mode']
    voice = ENUM['voice']
    skipped = set()
    i = 0

    for row in util.read_csv(ctx.config['PARTICIPLE_STEMS']):
        root = row['root']
        hom = row['hom']

        try:
            root_id = root_map[(root, hom)]
        except KeyError:
            skipped.add((root, hom))
            continue

        data = {
            'name': row['stem'],
            'root_id': root_id,
            'mode_id': mode[row['mode']],
            'voice_id': voice[row['voice']]
        }

        session.add(ParticipleStem(**data))

        i += 1
        if i % 100 == 0:
            util.tick(row['stem'])
            session.commit()

    session.commit()
    session.close()
    print('Skipped', len(skipped), 'roots.')


def add_nominal_endings(ctx):
    """Populates `NominalEnding`."""
    session = ctx.session
    gender = ENUM['gender']
    case = ENUM['case']
    number = ENUM['number']

    for row in util.read_csv(ctx.config['COMPOUNDED_NOMINAL_ENDINGS']):
        ending = NominalEnding(name=row['ending'],
                               stem_type=row['stem_type'],
                               gender_id=gender[row['form_gender']],
                               case_id=None, number_id=None, compounded=True)
        session.add(ending)

    seen = set()
    for row in util.read_csv(ctx.config['INFLECTED_NOMINAL_ENDINGS']):
        ending = NominalEnding(name=row['ending'],
                               stem_type=row['stem_type'],
                               gender_id=gender[row['form_gender']],
                               case_id=case[row['case']],
                               number_id=number[row['number']], compounded=False)
        session.add(ending)

        if row['stem_type'] not in seen:
            util.tick(row['stem_type'])
            seen.add(row['stem_type'])

    session.commit()
    session.close()


def add_nominal_stems(ctx):
    """Add regular noun stems to the database."""
    # Since there are so many nominal stems, the SQLAlchemy calls here
    # are a little more low-level.

    conn = ctx.engine.connect()
    ins = NominalStem.__table__.insert()
    gender_group = ENUM['gender_group']

    buf = []
    i = 0
    tick = util.tick_every(5000)
    for row in util.read_csv(ctx.config['NOMINAL_STEMS']):
        genders_id = gender_group[row['stem_genders']]

        buf.append({
            'name': row['stem'],
            'pos_id': Tag.NOMINAL,
            'genders_id': genders_id,
        })

        tick(row['stem'])
        i += 1
        if i % 500 == 0:
            conn.execute(ins, buf)
            buf = []

    # Add any remainder.
    if buf:
        conn.execute(ins, buf)


def add_irregular_nouns(ctx):
    """Add irregular nouns to the database."""

    session = ctx.session
    gender_group = ENUM['gender_group']
    gender = ENUM['gender']
    case = ENUM['case']
    number = ENUM['number']

    with open(ctx.config['IRREGULAR_NOUNS']) as f:
        for noun in yaml.load_all(f):
            genders_id = gender_group[noun['genders']]
            stem = NounStem(name=noun['name'], genders_id=genders_id)
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
    session.close()


def add_irregular_adjectives(ctx):
    """Add regular irregular adjectives to the database."""

    session = ctx.session
    gender = ENUM['gender']
    case = ENUM['case']
    number = ENUM['number']

    with open(ctx.config['IRREGULAR_ADJECTIVES']) as f:
        for adj in yaml.load_all(f):
            stem = AdjectiveStem(name=adj['name'])
            session.add(stem)
            session.flush()

            # Mark the stem as irregular
            complete = adj['complete']
            irreg = StemIrregularity(stem=stem, fully_described=complete)
            session.add(irreg)
            session.flush()

            util.tick(stem.name)

            for form in adj['forms']:
                name = form['name']
                gender_id = gender[form['gender']]
                case_id = case[form['case']]
                number_id = number[form['number']]

                result = Adjective(stem=stem, name=name, gender_id=gender_id,
                                   case_id=case_id, number_id=number_id)
                session.add(result)

    session.commit()
    session.close()


def add_pronouns(ctx):
    """Populates `PronounStem` and `Pronoun`."""

    session = ctx.session
    gender_group = ENUM['gender_group']
    gender = ENUM['gender']
    case = ENUM['case']
    number = ENUM['number']

    seen_stems = {}  # (stem, genders_id) -> id
    for row in util.read_csv(ctx.config['PRONOUNS']):
        stem = row['stem']
        genders_id = gender_group[row['stem_genders']]

        if (stem, genders_id) not in seen_stems:
            pronoun_stem = PronounStem(name=stem, genders_id=genders_id)
            session.add(pronoun_stem)
            session.flush()
            seen_stems[(stem, genders_id)] = pronoun_stem.id
            util.tick(stem)

        stem_id = seen_stems[(stem, genders_id)]
        session.add(Nominal(stem_id=stem_id, name=row['form'],
                            gender_id=gender[row['form_gender']],
                            case_id=case[row['case']],
                            number_id=number[row['number']]))
        session.flush()

    session.commit()
    session.close()


def run(ctx):
    """Create and populate tables in the database."""
    ctx.drop_all()
    ctx.create_all()

    util.heading('Metadata and sandhi')
    add_tags(ctx)
    add_enums(ctx)
    add_sandhi_rules(ctx)

    util.heading('Indeclinables (non-verbal)')
    add_indeclinables(ctx)

    util.heading('Verbal data')
    prefix_map = add_verb_prefixes(ctx)
    root_map = add_roots(ctx, prefix_map=prefix_map)
    add_verb_endings(ctx)
    add_verbs(ctx, root_map)
    add_participle_stems(ctx, root_map)
    add_verbal_indeclinables(ctx, root_map)
    del prefix_map

    util.heading('Nominal data')
    add_nominal_stems(ctx)
    add_nominal_endings(ctx)
    add_pronouns(ctx)
    # add_irregular_nouns(ctx)
    # add_irregular_adjectives(ctx)

    print('Done.')


if __name__ == '__main__':
    ctx = Context(sys.argv[1])
    run(ctx)
