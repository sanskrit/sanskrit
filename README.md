Sanskrit
========

This is a general-purpose package for dealing with Sanskrit data of any kind.
It currently operates on the sound and letter levels, with modules like:

- `sounds`, for testing sounds and getting the meter of a phrase
- `sanscript`, for transliterating Sanskrit from one script to another

Once these levels are working more solidly, the package will move up to the
word and sentence level and provide tools for inflecting, analyzing, tagging,
and parsing Sanskrit.

This is a port of an older package that featured a full part-of-speech tagger
and several powerful utilities for working iwith Sanskrit. But the old version
was brittle and suffered from a poor API. This rewrite hopes to fix the
original's problems, although it will borrow from it heavily wherever possible.
