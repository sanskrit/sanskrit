import yaml
import xml.etree.ElementTree as ET
from sanskrit.schema import *

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
            for rule in ruleset['rules']:
                rule['rule_type'] = mapper[rule_type]
                s = SandhiRule(**rule)
                session.add(s)

    session.commit()
    session.close()

def create_tables(ctx):
    Base.metadata.create_all(ctx.engine)

def run(ctx):
    """Run the main setup function."""
    session = ctx.session_class()

    create_tables(ctx)
    add_enums(session, ctx)
    add_sandhi(session, ctx)
