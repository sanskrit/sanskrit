Quickstart
==========

This page covers the most common use cases for the ``sanskrit`` package.


Building the database
---------------------

The ``sanskrit`` package is most useful when it can work with linguistic data.
Not all of the code in the `sanskrit` package requires access to this data,
but the most interesting code does. This data is managed internally as an SQL
database, but you don't need to know to know any SQL to work with it.

The database is initialized from a set of special data files. To get that data,
you can clone this repository from GitHub::

    git clone https://github.com/sanskrit/data.git

and run a script to prepare the data for use::

    cd data && python bin/make_data.py && cd -

After you run these two commands, the ``data/all-data`` folder will contain
CSV files that the ``sanskrit`` package can process directly.
:mod:`sanskrit.setup` loads these files into a database, which makes the data
they contain easier to query.

Currently, the easiest way to create this database is to run a script like the
following. You only need to run this once::

    from sanskrit import context, setup

    # Path to the 'all-data' folder you produced above.
    data_path = '/path/to/sanskrit/data/all-data'
    # Absolute path to where you want your sqlite database to be.
    sqlite_path = '/path/to/your/data.sqlite'

    ctx = context.Context({
        'DATABASE_URI': 'sqlite:///' + sqlite_path,
        'DATA_PATH': data_path
    })
    setup.run(ctx)

Here, ``context`` is a :class:`~sanskrit.context.Context`, which contains
information like the database URI and the locations of various data files.


Sounds and meter
----------------

TODO. For now, see :mod:`sanskrit.sounds`.

Sandhi rules
------------

TODO. For now, see :mod:`sanskrit.sandhi`.

Analyzing words
---------------

The :class:`~sanskrit.analyze.SimpleAnalyzer` class provides a way to analyze
Sanskrit words. By *analyze* we mean that the analyzer identifies the stem
or root of the word (if applicable) and provides useful information about how
it was inflected. By *word* we mean a finished Sanskrit *pada* (as opposed to
a stem or root). For example, this::

    from sanskrit import analyze
    a = analyze.SimpleAnalyzer(ctx)
    for item in a.analyze('anugacCati'):
        print item

would produce the following output::

    Verb(134712, u'anugacCati')
    Nominal(None, 'anugacCati')
    Nominal(None, 'anugacCati')

where the first result is an inflected verb and the next two results are
inflected participles with either masculine or neuter gender. You can inspect
these results for more information. For example, this::

    p = a.analyze('anugacCati')[1]
    print p.stem.name
    print p.stem.root.name
    print p.stem.mode.name
    print p.stem.voice.name

would produce the following output::

    anugacCat
    anugam
    present
    parasmaipada


Tagging text
------------

The :class:`~sanskrit.tagger.Tagger` class provides a way to analyze all of the
words in some Sanskrit passage. It does so by undoing the sandhi rules that
separate different words then analyzing each of those words for a good parse.
Since natural language is ambiguous, the tagger won't always produce "correct"
output. Instead, it will make its best guess.

For example, this::

    from sanskrit import tagger
    t = tagger.Tagger(ctx)
    for item in t.tag_segment('kAntAvirahaguruRA'):
        print item.form

would produce the following output::

    Nominal(None, 'kAntA')
    Nominal(None, 'viraha')
    Nominal(None, 'guruRA')

Currently, the tagger runs `greedily`. Future versions of the tagger will be
more sophisticated.

.. _greedily: http://en.wikipedia.org/wiki/Greedy_algorithm


Interactively tagging words
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Even the best tagger is liable to make mistakes. The ``shell`` module makes it
easy to fix these mistakes interactively. For example, this::

    from sanskrit import shell

    data = "Darmakzetre kurukzetre"
    shell.run(ctx, data)

would produce the following output::

    *--------------------------------------------------
    *
    * Interactive Sanskrit tagger
    *
    *--------------------------------------------------
    1  : get alternatives for form 1
    s  : re-split the chunk
    pc : previous chunk
    nc : next chunk
    q  : quit
    ?  : help
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Darmakzetre kurukzetre

    1 : ('Darmakzetre', 'nominal', u'Darmakzetra', u'm-7-s')

    :

where the last line is a prompt for user input.

The shell is still in its early stages and isn't very useful currently, but it
does give a feel for how the tagger and the analyzer work.
