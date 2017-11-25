# -*- coding: utf-8 -*-
"""
sanskrit.transliterate.betacode
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Transliteration functions for Greek. This module can convert a
`Beta Code`_ string to polytonic Greek.

The code uses the monotonic Greek 'tonos' for acute accents, per
`this discussion`_. The discussion mentions the preferred forms for
various accented letters:

========================================== ========== ===========
Character                                  Deprecated Preferred
========================================== ========== ===========
lowercase alpha + acute                    1F71       03AC
lowercase epsilon + acute                  1F73       03AD
lowercase eta + acute                      1F75       03AE
lowercase iota + acute                     1F77       03AF
lowercase omicron + acute                  1F79       03CC
lowercase upsilon + acute                  1F7B       03CD
lowercase omega + acute                    1F7D       03CE
lowercase iota + diaeresis + acute         1FD3       0390
lowercase upsilon + diaeresis + acute      1FE3       03B0
========================================== ========== ===========

Adapted from beta2unicode.py by `James Tauber <http://jtauber.com/>`_.
The original code is still `available`_.

.. _Beta Code:
    http://www.tlg.uci.edu/encoding/
.. _this discussion:
    http://socrates.berkeley.edu/~pinax/greekkeys/technicalDetails.html
.. _available:
    http://jtauber.com/blog/2005/01/27/betacode_to_unicode_in_python/

:license: MIT and BSD
"""

from __future__ import unicode_literals


class Trie(object):

    """A modified version of jtauber's original Trie."""

    def __init__(self):
        self.root = [None, {}]

    def __setitem__(self, key, value):
        curr_node = self.root
        for ch in key:
            curr_node = curr_node[1].setdefault(ch, [None, {}])
        curr_node[0] = value

    def findp(self, key):
        curr_node = self.root
        remainder = key
        for ch in key:
            try:
                curr_node = curr_node[1][ch]
            except KeyError:
                return (curr_node[0], remainder)
            remainder = remainder[1:]
        return (curr_node[0], remainder)

    def convert(self, keystring):
        valuestring = ""
        key = keystring
        while key:
            value, key = self.findp(key)
            if not value:
                return valuestring
            valuestring += value
        return valuestring


def beta2unicodeTrie():
    t = Trie()

    t["*A"] = "\u0391"
    t["*B"] = "\u0392"
    t["*G"] = "\u0393"
    t["*D"] = "\u0394"
    t["*E"] = "\u0395"
    t["*Z"] = "\u0396"
    t["*H"] = "\u0397"
    t["*Q"] = "\u0398"
    t["*I"] = "\u0399"
    t["*K"] = "\u039A"
    t["*L"] = "\u039B"
    t["*M"] = "\u039C"
    t["*N"] = "\u039D"
    t["*C"] = "\u039E"
    t["*O"] = "\u039F"
    t["*P"] = "\u03A0"
    t["*R"] = "\u03A1"
    t["*S"] = "\u03A3"
    t["*T"] = "\u03A4"
    t["*"] = "\u03A5"
    t["*F"] = "\u03A6"
    t["*X"] = "\u03A7"
    t["*Y"] = "\u03A8"
    t["*W"] = "\u03A9"
    t["*V"] = "\u03DC"

    t["A"] = "\u03B1"
    t["B"] = "\u03B2"
    t["G"] = "\u03B3"
    t["D"] = "\u03B4"
    t["E"] = "\u03B5"
    t["Z"] = "\u03B6"
    t["H"] = "\u03B7"
    t["Q"] = "\u03B8"
    t["I"] = "\u03B9"
    t["K"] = "\u03BA"
    t["L"] = "\u03BB"
    t["M"] = "\u03BC"
    t["N"] = "\u03BD"
    t["C"] = "\u03BE"
    t["O"] = "\u03BF"
    t["P"] = "\u03C0"
    t["R"] = "\u03C1"

    t["S\n"] = "\u03C2"
    t["S,"] = "\u03C2,"
    t["S."] = "\u03C2."
    t["S:"] = "\u03C2:"
    t["S;"] = "\u03C2;"
    t["S]"] = "\u03C2]"
    t["S@"] = "\u03C2@"
    t["S_"] = "\u03C2_"
    t["S"] = "\u03C3"

    t["T"] = "\u03C4"
    t["U"] = "\u03C5"
    t["F"] = "\u03C6"
    t["X"] = "\u03C7"
    t["Y"] = "\u03C8"
    t["W"] = "\u03C9"
    t["V"] = "\u03DD"

    t["I+"] = "\u03CA"
    t["U+"] = "\u03CB"

    t["A)"] = "\u1F00"
    t["A("] = "\u1F01"
    t["A)\\"] = "\u1F02"
    t["A(\\"] = "\u1F03"
    t["A)/"] = "\u1F04"
    t["A(/"] = "\u1F05"
    t["E)"] = "\u1F10"
    t["E("] = "\u1F11"
    t["E)\\"] = "\u1F12"
    t["E(\\"] = "\u1F13"
    t["E)/"] = "\u1F14"
    t["E(/"] = "\u1F15"
    t["H)"] = "\u1F20"
    t["H("] = "\u1F21"
    t["H)\\"] = "\u1F22"
    t["H(\\"] = "\u1F23"
    t["H)/"] = "\u1F24"
    t["H(/"] = "\u1F25"
    t["I)"] = "\u1F30"
    t["I("] = "\u1F31"
    t["I)\\"] = "\u1F32"
    t["I(\\"] = "\u1F33"
    t["I)/"] = "\u1F34"
    t["I(/"] = "\u1F35"
    t["O)"] = "\u1F40"
    t["O("] = "\u1F41"
    t["O)\\"] = "\u1F42"
    t["O(\\"] = "\u1F43"
    t["O)/"] = "\u1F44"
    t["O(/"] = "\u1F45"
    t["U)"] = "\u1F50"
    t["U("] = "\u1F51"
    t["U)\\"] = "\u1F52"
    t["U(\\"] = "\u1F53"
    t["U)/"] = "\u1F54"
    t["U(/"] = "\u1F55"
    t["W)"] = "\u1F60"
    t["W("] = "\u1F61"
    t["W)\\"] = "\u1F62"
    t["W(\\"] = "\u1F63"
    t["W)/"] = "\u1F64"
    t["W(/"] = "\u1F65"

    t["A)="] = "\u1F06"
    t["A(="] = "\u1F07"
    t["H)="] = "\u1F26"
    t["H(="] = "\u1F27"
    t["I)="] = "\u1F36"
    t["I(="] = "\u1F37"
    t["U)="] = "\u1F56"
    t["U(="] = "\u1F57"
    t["W)="] = "\u1F66"
    t["W(="] = "\u1F67"

    t["*A)"] = "\u1F08"
    t["*)A"] = "\u1F08"
    t["*A("] = "\u1F09"
    t["*(A"] = "\u1F09"
    #
    t["*(\A"] = "\u1F0B"
    t["*A)/"] = "\u1F0C"
    t["*)/A"] = "\u1F0C"
    t["*A(/"] = "\u1F0F"
    t["*(/A"] = "\u1F0F"
    t["*E)"] = "\u1F18"
    t["*)E"] = "\u1F18"
    t["*E("] = "\u1F19"
    t["*(E"] = "\u1F19"
    #
    t["*(\E"] = "\u1F1B"
    t["*E)/"] = "\u1F1C"
    t["*)/E"] = "\u1F1C"
    t["*E(/"] = "\u1F1D"
    t["*(/E"] = "\u1F1D"

    t["*H)"] = "\u1F28"
    t["*)H"] = "\u1F28"
    t["*H("] = "\u1F29"
    t["*(H"] = "\u1F29"
    t["*H)\\"] = "\u1F2A"
    t[")\\*H"] = "\u1F2A"
    t["*)\\H"] = "\u1F2A"
    #
    t["*H)/"] = "\u1F2C"
    t["*)/H"] = "\u1F2C"
    #
    t["*)=H"] = "\u1F2E"
    t["(/*H"] = "\u1F2F"
    t["*(/H"] = "\u1F2F"
    t["*I)"] = "\u1F38"
    t["*)I"] = "\u1F38"
    t["*I("] = "\u1F39"
    t["*(I"] = "\u1F39"
    #
    #
    t["*I)/"] = "\u1F3C"
    t["*)/I"] = "\u1F3C"
    #
    #
    t["*I(/"] = "\u1F3F"
    t["*(/I"] = "\u1F3F"
    #
    t["*O)"] = "\u1F48"
    t["*)O"] = "\u1F48"
    t["*O("] = "\u1F49"
    t["*(O"] = "\u1F49"
    #
    #
    t["*(\O"] = "\u1F4B"
    t["*O)/"] = "\u1F4C"
    t["*)/O"] = "\u1F4C"
    t["*O(/"] = "\u1F4F"
    t["*(/O"] = "\u1F4F"
    #
    t["*U("] = "\u1F59"
    t["*("] = "\u1F59"
    #
    t["*(/"] = "\u1F5D"
    #
    t["*(="] = "\u1F5F"

    t["*W)"] = "\u1F68"
    t["*W("] = "\u1F69"
    t["*(W"] = "\u1F69"
    #
    #
    t["*W)/"] = "\u1F6C"
    t["*)/W"] = "\u1F6C"
    t["*W(/"] = "\u1F6F"
    t["*(/W"] = "\u1F6F"

    t["*A)="] = "\u1F0E"
    t["*)=A"] = "\u1F0E"
    t["*A(="] = "\u1F0F"
    t["*W)="] = "\u1F6E"
    t["*)=W"] = "\u1F6E"
    t["*W(="] = "\u1F6F"
    t["*(=W"] = "\u1F6F"

    t["A\\"] = "\u1F70"
    t["A/"] = "\u03AC"
    t["E\\"] = "\u1F72"
    t["E/"] = "\u03AD"
    t["H\\"] = "\u1F74"
    t["H/"] = "\u03AE"
    t["I\\"] = "\u1F76"
    t["I/"] = "\u03AF"
    t["O\\"] = "\u1F78"
    t["O/"] = "\u03CC"
    t["U\\"] = "\u1F7A"
    t["U/"] = "\u03CD"
    t["W\\"] = "\u1F7C"
    t["W/"] = "\u03CE"

    t["A)/|"] = "\u1F84"
    t["A(/|"] = "\u1F85"
    t["H)|"] = "\u1F90"
    t["H(|"] = "\u1F91"
    t["H)/|"] = "\u1F94"
    t["H)=|"] = "\u1F96"
    t["H(=|"] = "\u1F97"
    t["W)|"] = "\u1FA0"
    t["W(=|"] = "\u1FA7"

    t["A="] = "\u1FB6"
    t["H="] = "\u1FC6"
    t["I="] = "\u1FD6"
    t["U="] = "\u1FE6"
    t["W="] = "\u1FF6"

    t["I\\+"] = "\u1FD2"
    t["I/+"] = "\u0390"
    t["I+/"] = "\u0390"
    t["U\\+"] = "\u1FE2"
    t["U/+"] = "\u03B0"

    t["A|"] = "\u1FB3"
    t["A/|"] = "\u1FB4"
    t["H|"] = "\u1FC3"
    t["H/|"] = "\u1FC4"
    t["W|"] = "\u1FF3"
    t["W|/"] = "\u1FF4"
    t["W/|"] = "\u1FF4"

    t["A=|"] = "\u1FB7"
    t["H=|"] = "\u1FC7"
    t["W=|"] = "\u1FF7"

    t["R("] = "\u1FE4"
    t["*R("] = "\u1FEC"
    t["*(R"] = "\u1FEC"

#    t["~"] = "~"
#    t["-"] = "-"

#    t["(null)"] = "(null)"
#    t["&"] = "&"

    t["0"] = "0"
    t["1"] = "1"
    t["2"] = "2"
    t["3"] = "3"
    t["4"] = "4"
    t["5"] = "5"
    t["6"] = "6"
    t["7"] = "7"
    t["8"] = "8"
    t["9"] = "9"

    t["@"] = "@"
    t["$"] = "$"

    t[" "] = " "

    t["."] = "."
    t[","] = ","
    t["'"] = "'"
    t[":"] = ":"
    t[";"] = ";"
    t["_"] = "_"

    t["["] = "["
    t["]"] = "]"

    t["\n"] = ""

    return t


trie = beta2unicodeTrie()


def transliterate(beta):
    """Transliterate the given string from Beta Code to polytonic Greek.

    :param beta: some betacode string"""

    if beta.endswith('S'):
        # "to get final sigma, string must end in \n"
        beta += '\n'
    return trie.convert(beta)
