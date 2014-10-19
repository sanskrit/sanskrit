# -*- coding: utf-8 -*-
"""
    sanskrit.sandhi
    ~~~~~~~~~~~~~~~

    Sandhi operations.

    :license: MIT and BSD
"""

from . import sounds
from .schema import SandhiRule
from .util import HashTrie


class Exempt(unicode):

    """A helper class for marking strings as exempt from sandhi changes. To
    mark a string as exempt, just do the following::

        original = 'amI'
        exempt = Exempt('amI')

    :class:`Exempt` is a subclass of :class:`unicode`, so you can use normal
    string methods on :class:`Exempt` objects.
    """


class Sandhi(object):

    """Handles the phonetic rules that apply when Sanskrit words come together
    or split apart. The two main methods here are :meth:`splits` and
    :meth:`join`.
    """

    def __init__(self, rules=None):
        """"""
        self.splitter = HashTrie()
        self.joiner = {}
        if rules:
            self.add_rules(rules)

    def load(self, ctx):
        """Add rules from the database.

        :param ctx: the current :class:`~sanskrit.context.Context`.
        """
        self.add_rules(*self._query(ctx))

    def _query(self, ctx):
        """Query for :class:`SandhiRule`s and yield each as a
        :class:`dict`."""
        for rule in ctx.session.query(SandhiRule):
            yield (rule.first, rule.second, rule.result)

    def add_rules(self, *rules):
        """Add rules for splitting and joining words. Rules should be ordered
        collections that contain:

        - the first part of the combination
        - the second part of the combination
        - the result

        An example::

            rule = ('a', 'i', 'e')

        :param rules: a list of rules
        """
        for first, second, result in rules:
            self.joiner[(first, second)] = result

            result = result.replace(' ', '')
            items = (first, second, result, len(first), len(second),
                     len(result))
            self.splitter[result] = items

    @staticmethod
    def internal_retroflex(term):
        """Apply the "n -> ṇ" and "s -> ṣ" rules of internal sandhi.

        :param term: the term to process
        """
        # causes "s" retroflexion
        s_trigger = set('iIuUfFeEoOkr')
        # causes "n" retroflexion
        n_trigger = set('fFrz')
        # Allowed after n_trigger
        n_between = sounds.VOWELS.union('kKgGNpPbBmhvyM')
        # Must appear after the retroflexed "n"
        n_after = sounds.VOWELS.union('myvn')
        # Defines t retroflexion
        retroflexion_dict = dict(zip('tT', 'wW'))

        letters = list(term)

        apply_s = False
        apply_n = False
        had_n = False  # Used for double retroflexion ('nisanna' -> 'nizaRRa')
        had_s = False  # Used for 't' retroflexion
        for i, L in enumerate(letters[:-1]):
            # "t" retroflexion after "s" retroflexion
            if had_s:
                had_s = False
                letters[i] = retroflexion_dict.get(L, L)

            # "s" retroflexion
            if apply_s and L == 's':
                letters[i] = L = 'z'
                had_s = True
            apply_s = L in s_trigger

            # "n" retroflexion
            if had_n and L == 'n':
                letters[i] = 'R'
                had_n = False
            elif apply_n and L == 'n' and letters[i + 1] in n_after:
                letters[i] = 'R'
                had_n = True
            if L in n_trigger:
                apply_n = True
            else:
                apply_n = apply_n and L in n_between

        return ''.join(letters)

    def join(self, *chunks, **kw):
        """Join the given chunks according to the object's rules::

            assert 'tasyecCA' == s.join('tasya', 'icCA')

        :meth:`join` does **not** take pragṛhya rules into account. As a
        reminder, the main exception are:

            | 1.1.11 "ī", "ū", and "e" when they end words in the dual.
            | 1.1.12 the same vowels after the "m" of adas;
            | 1.1.13 particles with just one vowel, apart from "ā"
            | 1.1.14 particles that end in "o".

        One simple way to account for these rules is to wrap exempt strings
        with :class:`Exempt`::

            assert 'ta iti' == s.join('te', 'iti')
            assert 'te iti' == s.join(Exempt('te'), 'iti')

        :param chunks: the chunks to stitch together
        :key internal: the separator to use between non-joined terms. By
                        default, this is a single space ``' '``. For internal
                        sandhi, this should be set to ``''``.
        """
        internal = kw.pop('internal', False)

        if kw:
            key = kw.keys()[0]
            msg = "'join() got an unexpected keyword argument '%s'" % key
            raise TypeError(msg)

        separator = '' if internal else ' '

        it = iter(chunks)
        returned = next(it)
        for chunk in it:
            if not chunk:
                continue
            if isinstance(returned, Exempt):
                returned += separator + chunk
            else:
                # `i` controls the number of letters to grab from the end of
                # the first word. For most rules, one letter is sufficient.
                # But visarga sandhi needs slightly more context.
                for i in (2, 1, 0):
                    if not i:
                        returned += separator + chunk
                        break
                    key = (returned[-i:], chunk[0])
                    result = self.joiner.get(key, None)
                    if result:
                        returned = returned[:-i] + result + chunk[1:]
                        break
            if isinstance(chunk, Exempt):
                returned = Exempt(returned)

        if internal:
            return Sandhi.internal_retroflex(returned)
        else:
            return returned

    def splits(self, chunk):
        """Return a generator for all splits in `chunk`. Results are yielded
        as 2-tuples containing the term before the split and the term after::

            for item in s.splits('nareti'):
                before, after = item

        :meth:`splits` will generate many false positives, usually when the
        first part of the split ends in an invalid consonant::

            assert ('narAv', 'iti') in s.splits('narAviti')

        These should be filtered out in the calling function.

        Splits are generated from left to right, but the function makes no
        guarantees on when certain rules are applied. That is, output is
        loosely ordered but nondeterministic.
        """

        splitter = self.splitter
        chunk_len = len(chunk)

        for i in xrange(chunk_len):
            # Default split: chop the chunk in half with no other changes.
            # This can yield a lot of false positives.
            chunk1, chunk2 = chunk[:i], chunk[i:]
            if i:
                yield (chunk1, chunk2)

            # Rule-based splits: undo a sandhi change
            rules = splitter[chunk2]
            for first, second, result, _, _, len_result in rules:
                before = chunk1 + first
                after = second + chunk2[len_result:]
                yield (before, after)

        # Non-split: yield the chunk as-is.
        yield (chunk, '')

    def split_off(self, chunk, fragment):
        """Remove `fragment` from the end of `chunk` and yield the results.
        If `fragment` cannot be found, yield nothing.

        :param chunk: the phrase to split
        :param fragment: the phrase to split off
        """
        for before, after in self.splits(chunk):
            if after == fragment:
                yield before
