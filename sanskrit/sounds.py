# -*- coding: utf-8 -*-
"""
sanskrit.language.sounds
~~~~~~~~~~~~~~~~~~~~~~~~

Everything to do with Sanskrit sounds.

:license: MIT and BSD
"""

ALL = set("aAiIuUfFxXeEoOMHkKgGNcCjJYwWqQRtTdDnpPbBmyrlvSzsh '~")

VOWELS = set('aAiIuUfFxXeEoO')
SHORT_VOWELS = set('aiufx')
LONG_VOWELS = VOWELS - SHORT_VOWELS

STOPS = set('kKgGcCjJwWqQtTdDpPbB')
NASALS = set('NYRnm')
SEMIVOWELS = set('yrlLv')
SAVARGA = set('Szsh')
CONSONANTS = STOPS.union(NASALS).union(SEMIVOWELS).union(SAVARGA)

SOUNDS = VOWELS.union(CONSONANTS).union(set('HM'))

ASPIRATED_STOPS = set('KGCJWQTDPB')
VOICED_ASPIRATED_STOPS = set('GJQDB')
UNASPIRATED_STOPS = STOPS - ASPIRATED_STOPS
RETROFLEXES = set('wWqQRz')

VOICED_SOUNDS = set('aAiIuUfFxXeEoOgGNjJYqQRdDnbBmyrlvh')
VALID_FINALS = set('aAiIuUfeEoOkwtpNnmsr')


# General functions
# -----------------

def clean(phrase, valid=None):
    """Remove all characters from `phrase` that are not in `valid`.

    :param phrase: the phrase to clean
    :param valid: the set of valid characters. By default, this includes
                  all letters in the SLP1 alphabet, as well as ``'``, ``~``,
                  and the space character.
    """
    valid = valid or ALL
    return ''.join([L for L in phrase if L in valid])


def key_fn(s):
    """Sorting function for Sanskrit words in SLP1."""
    sa = "aAiIuUfFxXeEoOMHkKgGNcCjJYwWqQRtTdDnpPbBmyrlvSzsh '~"
    en = "123ABCDEFGHIJKLMNOPQRSTUVWabcdefghijklmnopqrstuvwxyz"
    mapper = dict(zip(sa, en))
    mapped = map(mapper.__getitem__, [x for x in s if x in ALL])
    return ''.join(mapped)


# Letter transformations
# ----------------------

def letter_transform(name, docstring=None):
    data = {
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
        'simplify': dict(zip('kgGNhjtTdDpPbBnmsrH',
                             'kkkkkwttttppppnmHHH')),
        'guna': dict(zip('i I u U  f  F  x  X'.split(),
                         'e e o o ar ar al al'.split())),
        'vrddhi': dict(zip('a i I u U  f  F  x  X e o'.split(),
                           'A E E O O Ar Ar Al Al E O'.split()))
    }

    get = data[name].get

    def func(L):
        return get(L, L)

    if docstring is None:
        docstring = """{0} `letter`. If this is not possible, return `letter`
        unchanged.

        :param letter: the letter to {1}
        """.format(name.capitalize(), name)

    func.__name__ = name
    func.__doc__ = docstring
    return func

aspirate = letter_transform('aspirate')
deaspirate = letter_transform('deaspirate')
voice = letter_transform('voice')
devoice = letter_transform('devoice')
nasalize = letter_transform('nasalize')
dentalize = letter_transform('dentalize')
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

del letter_transform


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
    for L in clean(phrase, SOUNDS)[::-1]:
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
