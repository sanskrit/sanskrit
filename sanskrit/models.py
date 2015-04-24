"""
    sanskrit.models
    ~~~~~~~~~~~~~~~

    Statistical models.

    :license: MIT
"""
from __future__ import division
import collections
import itertools
import math


#: Marks the beginning or end of a sequence.
SEQUENCE_BOUNDARY = '__SEQ_BOUNDARY__'


class SequenceModel:

    """A bigram model over sequences of events."""

    def __init__(self):
        self.prior = collections.Counter()
        self.joint = collections.Counter()

    def _iter_ngrams(self, seq, size):
        iters = itertools.tee(seq, size)
        for i in xrange(1, size):
            for each in iters[i:]:
                next(each, None)
        return itertools.izip(*iters)

    def insert(self, seq):
        """
        :param seq: a list of events
        """
        seq = itertools.chain([SEQUENCE_BOUNDARY], seq, [SEQUENCE_BOUNDARY])
        for x, y in self._iter_ngrams(seq, 2):
            self.joint[(x, y)] += 1
            self.prior[x] += 1

    def log_cond_prob(self, xs, y, delta=1):
        """Return log(P(y | xs)) with add-`delta` smoothing.

        P(y | xs) is approximated as P(y | xs[-1]).

        :param y: the posterior event
        :param xs: all prior events
        """
        x_n = xs[-1] if len(xs) else None
        numerator = self.joint[(x_n, y)] + delta
        denominator = self.prior[x_n] + len(self.prior.keys())
        assert denominator > 0
        return math.log(numerator / denominator)
