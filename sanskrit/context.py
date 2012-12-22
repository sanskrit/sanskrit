# -*- coding: utf-8 -*-
import imp
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from .schema import Base, EnumBase


class Context(object):

    """The package context. In addition to storing basic config information,
    such as the database URI or paths to various data files, a :class:`Context`
    also constructs a :class:`~sqlalchemy.orm.session.Session` class for
    connecting to the database.

    You can populate a context in several ways. For example, you can pass a
    path to a Python module::

        context = Context('project/config.py')

    If you do so, only uppercase keys will be stored in the context. This lets
    you use lowercase variables as temporary values.

    Config values are stored internally as a :class:`dict`, so you can always
    just use ordinary :class:`dict` methods::

        context.config['FOO'] = 'baz'

    :param config: an object to read from. If this is a string, treat
                   `config` as a module path and load values from that
                   module. Otherwise, treat `config` as a dictionary.
    """

    def __init__(self, config=None, connect=True):
        #: A :class:`dict` of various settings. By convention, all keys are
        #: uppercase. These are used to create :attr:`engine` and
        #: :attr:`session_class`.
        self.config = {}

        #: The :class:`~sqlalchemy.engine.base.Engine` that underlies
        #: :attr:`session_class`.
        self.engine = None

        #: A :class:`~sqlalchemy.orm.session.Session` class.
        self.session_class = None

        if isinstance(config, basestring):
            filepath = config
            config = imp.new_module('config')
            config.__file__ = filepath
            try:
                execfile(filepath, config.__dict__)
            except IOError, e:
                e.strerror = 'Cannot load config file: %s' % e.strerror
                raise

        try:
            config = config or {}
            for key in config:
                if key.isupper():
                    self.config[key] = config[key]
        except TypeError:
            for key in dir(config):
                if key.isupper():
                    self.config[key] = getattr(config, key)

        def default(name, *args):
            path = os.path.join(self.config['DATA_PATH'], *args)
            self.config.setdefault(name, path)

        default('MONIER_XML_PATH', 'mw', 'monier.xml')

        default('NOUN_DATA', 'nominal', 'nouns.yml')
        default('ADJECTIVE_DATA', 'nominal', 'adjectives.yml')
        default('PRONOUN_DATA', 'nominal', 'pronouns.yml')
        default('IRREGULAR_NOUN_DATA', 'nominal', 'irregular-nouns.yml')

        default('ROOT_DATA', 'verbal', 'roots.yml')
        default('PREFIXED_ROOT_DATA', 'verbal', 'prefixed-roots.yml')
        default('VERB_STEM_DATA', 'verbal', 'stems.yml')
        default('VERB_ENDING_DATA', 'misc', 'verb-endings.yml')
        default('VERB_DATA', 'verbal', 'verbs.yml')

        default('ENUM_DATA', 'misc', 'enums.yml')
        default('INDECLINABLE_DATA', 'misc', 'indeclinables.yml')
        default('VERB_PREFIX_DATA', 'misc', 'verb-prefixes.yml')
        default('SANDHI_DATA', 'misc', 'sandhi.yml')
        default('NOMINAL_ENDING_DATA', 'misc', 'nominal-endings.yml')

        if connect and 'DATABASE_URI' in self.config:
            self.connect()

    def build(self):
        """Build all data."""
        from sanskrit import setup
        setup.run(self)

    def connect(self):
        """Connect to the database."""
        self.engine = create_engine(self.config['DATABASE_URI'])
        self.session_class = scoped_session(sessionmaker(autocommit=False,
                                                         autoflush=False,
                                                         bind=self.engine))

    def create_all(self):
        """Create tables for every model in `sanskrit.schema`."""
        metadata = Base.metadata
        extant = {t.name for t in metadata.tables.values() if t.exists(self.engine)}
        metadata.create_all(self.engine)
        for name in metadata.sorted_tables:
            if name not in extant:
                print '  [ c ] {0}'.format(name)

    def drop_all(self):
        """Drop all tables defined in `sanskrit.schema`."""
        Base.metadata.drop_all(self.engine)

    def _build_enums(self):
        """Fetch and store enumerated data."""
        self._enum_id = {}
        self._enum_abbr = {}
        session = self.session_class()
        for cls in EnumBase.__subclasses__():
            key = cls.__tablename__
            self._enum_id[key] = enum_id = {}
            self._enum_abbr[key] = enum_abbr = {}
            for item in session.query(cls).all():
                enum_id[item.name] = enum_id[item.abbr] = item.id
                enum_abbr[item.id] = enum_abbr[item.name] = item.abbr

    @property
    def enum_id(self):
        """Maps a name or abbreviation to an ID."""
        try:
            return self._enum_id
        except AttributeError:
            self._build_enums()
            return self._enum_id

    @property
    def enum_abbr(self):
        """Maps an ID or name to an abbreviation."""
        try:
            return self._enum_abbr
        except AttributeError:
            self._build_enums()
            return self._enum_abbr
