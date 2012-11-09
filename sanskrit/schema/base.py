# -*- coding: utf-8 -*-
"""
sanskrit.schema.base
~~~~~~~~~~~~~~~~~~~~

Base classes for various models.
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base, declared_attr

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

    def __repr__(self):
        cls = self.__class__.__name__
        return "%s(%r, %r)" % (cls, self.id, self.name)
