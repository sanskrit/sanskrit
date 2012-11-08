import yaml
from sanskrit.db.schema import *

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
                Gender, Case]:
        for key in dir(cls):
            if key.isupper():
                id = getattr(cls, key)
                session.add(cls(id=id, name=key.lower()))

    session.commit()

def run(ctx):
    """Run the main setup function."""
    session = ctx.session_class()
    Base.metadata.create_all(ctx.engine)

    add_enums(session, ctx)
