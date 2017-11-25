# -*- coding: utf-8 -*-
"""
    sanskrit.sounds
    ~~~~~~~~~~~~~~~

    Code for checking and transforming Sanskrit sounds. This module also
    contains basic metrical functions (see :func:`sanskrit.sounds.meter`
    and :func:`sanskrit.sounds.num_syllables`).

    All functions assume SLP1.

    :license: MIT
"""

#: All legal sounds, including anusvara, ardhachandra, and Vedic `'L'`.
from builtins import map
from builtins import zip
ALL_SOUNDS = frozenset("aAiIuUfFxXeEoOMHkKgGNcCjJYwWqQRtTdDnpPbBmyrlLvSzsh'~")

#: All legal tokens, including sounds, punctuation (`'|'`), and whitespace.
ALL_TOKENS = ALL_SOUNDS | {'|', ' ', '\n'}

#: All vowels.
VOWELS = frozenset('aAiIuUfFxXeEoO')

#: Short vowels.
SHORT_VOWELS = frozenset('aiufx')

#: Stop consonants.
STOPS = frozenset('kKgGcCjJwWqQtTdDpPbB')

#: Nasals.
NASALS = frozenset('NYRnm')

#: Semivowels.
SEMIVOWELS = frozenset('yrlLv')

#: Savarga
SAVARGA = frozenset('Szsh')

#: Consonants.
CONSONANTS = STOPS.union(NASALS).union(SEMIVOWELS).union(SAVARGA)

#: Valid word-final sounds.
VALID_FINALS = frozenset('aAiIuUfeEoOkwtpNnmsr')


# General functions
# -----------------

def clean(phrase, valid):
    """Remove all characters from `phrase` that are not in `valid`.

    :param phrase: the phrase to clean
    :param valid: the set of valid characters. A sensible default is
                  `sounds.ALL_TOKENS`.
    """
    return ''.join([L for L in phrase if L in valid])


def key_fn(s):
    """Sorting function for Sanskrit words in SLP1."""
    sa = "aAiIuUfFxXeEoOMHkKgGNcCjJYwWqQRtTdDnpPbBmyrlvSzsh '~"
    en = "123ABCDEFGHIJKLMNOPQRSTUVWabcdefghijklmnopqrstuvwxyz"
    mapper = dict(zip(sa, en))
    mapped = map(mapper.__getitem__, [x for x in s if x in ALL_SOUNDS])
    return ''.join(mapped)


# Letter transformations
# ----------------------

def letter_transform(name, docstring=None):
    data = {
        'shorten': dict(zip('AIUFX', 'aiufx')),
        'lengthen': dict(zip('aiufx', 'AIUFX')),
        'semivowel': dict(zip('iIuUfFxXeEoO',
                              'y y v v r r l l ay Ay av Av'.split())),
        'aspirate': dict(zip('kgcjwqtdpb',
                             'KGCJWQTDPB')),
        'deaspirate': dict(zip('KGCJWQTDPB',
                               'kgcjwqtdpb')),
        'voice': dict(zip('kKcCwWtTpP',
                          'gGjJqQdDbB')),
        'devoice': dict(zip('gGjJqQdDbB',
                            'kKcCwWtTpP')),
        'nasalize': dict(zip('kKgGhcCjJwWqQtTdDpPbB',
                             'NNNNNYYYYRRRRnnnnmmmm')),
        'dentalize': dict(zip('wWqQRz',
                              'tTdDns')),
        'retroflex': dict(zip('tTdDns',
                              'wWqQRz')),
        'simplify': dict(zip('kgGNhjtTdDpPbBnmsrH',
                             'kkkkkwttttppppnmHHH')),
        'guna': dict(zip('i I u U  f  F  x  X'.split(),
                         'e e o o ar ar al al'.split())),
        'vrddhi': dict(zip('a i I u U  f  F  x  X e o'.split(),
                           'A E E O O Ar Ar Al Al E O'.split())),
        'samprasarana': dict(zip('yrlv', 'ifxu'))
    }

    get = data[name].get

    def func(L):
        return get(L, L)

    if docstring is None:
        docstring = """{0} `L`. If this is not possible, return `L` unchanged.

        :param L: the letter to {1}
        """.format(name.capitalize(), name)

    func.__name__ = name
    func.__doc__ = docstring
    return func


shorten = letter_transform('shorten')
lengthen = letter_transform('lengthen')
semivowel = letter_transform('semivowel')
aspirate = letter_transform('aspirate')
deaspirate = letter_transform('deaspirate')
voice = letter_transform('voice')
devoice = letter_transform('devoice')
nasalize = letter_transform('nasalize')
dentalize = letter_transform('dentalize')
retroflex = letter_transform('retroflex')
simplify = letter_transform('simplify',
                            docstring="""
    Simplify the given letter, if possible.

    Here, to "simplify" a letter is to reduce it to a sound that is permitted
    to end a Sanskrit word. For instance, the `c` in `vAc` should be reduced
    to `k`::

        assert simplify('c') == 'k'

    :param letter: the letter to simplify
    """
                            )


guna = letter_transform('guna',
                        docstring="""
    Apply guna to the given letter, if possible.
    """
                        )


vrddhi = letter_transform('vrddhi',
                          docstring="""
    Apply vrddhi to the given letter, if possible.
    """
                          )


samprasarana = letter_transform('samprasarana',
                                docstring="""
    Apply samprasarana to the given letter, if possible.
    """
                                )

del letter_transform


# Term transformations
# --------------------

class Term(str):

    def simplify(self):
        """Simplify the given string using consonant reduction."""
        return self[:-1] + simplify(self[-1])


# Meter and metrical properties
# -----------------------------

def num_syllables(phrase):
    """Find the number of syllables in `phrase`.

    :param phrase: the phrase to test
    """
    return sum(1 for L in phrase if L in VOWELS)


def meter(phrase, heavy='_', light='.'):
    """Find the meter of the given phrase. Results are returned as a list
    whose elements are either `heavy` and `light`.

    By the traditional definition, a syllable is **heavy** if one of the
    following is true:

    - the vowel is long
    - the vowel is short and followed by multiple consonants
    - the vowel is followed by an anusvara or visarga

    All other syllables are **light**.

    :param phrase: the phrase to scan
    :param heavy: used to indicate heavy syllables. By default it's a string,
                  but you can pass in anything.
    :param light: used to indicate light syllables. By default it's a string,
                   but you can pass in anything.
    """
    scan = []
    had_consonant = False

    # True iff we've seen an anusvara, a visarga, or some conjunct consonants
    saw_cluster = False
    append = scan.append

    # Search for heavy syllable and call all other syllables light. Since
    # syllable weight can depend on later consonants, we have to look ahead
    # to determine the proper weight. An easy way to do that is to reverse
    # the string:
    for L in clean(phrase, ALL_SOUNDS)[::-1]:
        if L in VOWELS:
            if saw_cluster or L not in SHORT_VOWELS:
                append(heavy)
            else:
                append(light)

            saw_cluster = False

        elif L in 'MH' or had_consonant:
            saw_cluster = True
        had_consonant = L in CONSONANTS

    return scan[::-1]
