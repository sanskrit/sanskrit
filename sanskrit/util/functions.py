"""
sanskrit.util.functions
~~~~~~~~~~~~~~~~~~~~~~~

Various helper functions.

:license: MIT and BSD
"""

def heading(s):
    """Print `s` as a heading. This is used to update the user during a
    long-running function."""
    print s
    print '-' * len(s)

def tick(s):
    """Print `s` as a list item. This is used to update the user during a
    long-running function.
    """
    print ' -', s
