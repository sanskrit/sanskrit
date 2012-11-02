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
CONSONANTS = STOPS.union(NASALS).union(SEMIVOWELS).union(set('Szsh'))

SOUNDS = VOWELS.union(CONSONANTS).union(set('HM'))

ASPIRATED_STOPS = set('KGCJWQTDPB')
VOICED_ASPIRATED_STOPS = set('GJQDB')
UNASPIRATED_STOPS = STOPS - ASPIRATED_STOPS
RETROFLEXES = set('wWqQRz')

VOICED_SOUNDS = set('aAiIuUfFxXeEoOgGNjJYqQRdDnbBmyrlvh')
VALID_FINALS = set('aAiIuUfeEoOkwtpNnmsr')


def clean(phrase, valid=ALL):
    """Remove all characters that are not in `valid`."""
    return ''.join([L for L in phrase if L in valid])

def num_syllables(phrase):
    """Count the number of syllables in `phrase`."""
    return sum(1 for L in phrase if L in VOWELS )

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
