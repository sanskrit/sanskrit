"""
    sanskrit.models
    ~~~~~~~~~~~~~~~

    Statistical models.

    :license: MIT
"""
from __future__ import division
from builtins import next, zip, range
import collections
import itertools
import math


#: Marks the beginning or end of a sequence.
SEQUENCE_BOUNDARY = '__SEQ_BOUNDARY__'


class SequenceModel(object):

    """A bigram model over sequences of events."""

    def __init__(self):
        self.prior = collections.Counter()
        self.joint = collections.Counter()
        self.num_prior_events = 80   #TODO: don't hard code

    def _iter_ngrams(self, seq, size):
        iters = itertools.tee(seq, size)
        for i in range(1, size):
            for each in iters[i:]:
                next(each, None)
        return zip(*iters)

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
        denominator = self.prior[x_n] + self.num_prior_events
        assert denominator > 0
        return math.log(numerator / denominator)


class FeatureModel(object):

    """Assigns a score using a small set of features."""

    def score(self, item, remainder):
        is_form = item.form.__class__.__name__ != 'NonForm'
        if is_form:
            item_len = len(item.form.name) if is_form else 0
            finished_chunk = 0 if remainder else 1
            return item_len + finished_chunk
        else:
            return 0
