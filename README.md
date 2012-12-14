Sanskrit
========

This is a general-purpose package for dealing with Sanskrit data of any kind.
It currently operates at and below the word level and below, with modules like:

- `query`, for accessing linguistic data
- `sandhi`, for applying and undoing sandhi changes
- `sounds`, for testing sounds and getting the meter of a phrase
- `sanscript`, for transliterating Sanskrit from one script to another

Soon the package will move up to the word and sentence levels. Once there, it
will provide tools for inflecting, analyzing, tagging, and parsing Sanskrit.

This is a port of an older package that featured a full part-of-speech tagger
and several powerful utilities for working with Sanskrit. But the old version
was brittle and suffered from a poor API. This rewrite hopes to fix the
original's problems. Still, it will borrow from it heavily wherever possible.
