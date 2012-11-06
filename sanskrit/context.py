# -*- coding: utf-8 -*-
import imp
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

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

    :param config: an object to read from. If this is a string, treat `config`
                as a module path and load values from that module. Otherwise,
                treat `config` as some sort of dictionary.
    """

    def __init__(self, config=None):
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

        DATA_PATH = self.config['DATA_PATH']
        default = self.config.setdefault
        join = os.path.join
        default('MONIER_XML_PATH', join(DATA_PATH, 'mw', 'monier.xml'))

        self.engine = create_engine(self.config['DATABASE_URI'])
        self.session_class = scoped_session(sessionmaker(autocommit=False,
                                                         autoflush=False,
                                                         bind=self.engine))
