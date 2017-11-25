"""
sanskrit.util.functions
~~~~~~~~~~~~~~~~~~~~~~~

Various helper functions.

:license: MIT and BSD
"""

from __future__ import print_function
import csv


def read_csv(filename):
    """Read from a CSV file using a DictReader.

    :param filename: the name of the file
    """
    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row


def heading(s, char='-'):
    """Print `s` as a heading. This is used to update the user during a
    long-running function."""
    print()
    print(s)
    print(char * len(s))


def tick(s):
    """Print `s` as a list item. This is used to update the user during a
    long-running function.
    """
    print(' -', s)


def tick_every(n):
    def func(x):
        func.i += 1
        if func.i % n == 0:
            print(func.i, ':', x)
    func.i = 0
    return func
