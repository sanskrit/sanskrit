# -*- coding: utf-8 -*-
"""
sanskrit.schema.sandhi
~~~~~~~~~~~~~~~~~~~~~~

Schema for sandhi rules.
"""

from sqlalchemy import Column, ForeignKey, Integer, String
from .base import Base, SimpleBase

class SandhiType(SimpleBase):

    """Rule type. Sandhi occurs in various contexts. In addition to some
    *general* rules, there are *internal* rules that apply between morphemes
    and *external* rules that apply between words.
    """

    GENERAL = 1
    INTERNAL = 2
    EXTERNAL = 3


class SandhiRule(Base):

    __tablename__ = 'sandhi'
    id = Column(Integer, primary_key=True)
    first = Column(String)
    second = Column(String)
    result = Column(String)
    rule_type = Column(ForeignKey(SandhiType.id))

    def __repr__(self):
        values = (self.id, self.first, self.second, self.result)
        return 'SandhiRule(%r, %r, %r, %r)' % values
