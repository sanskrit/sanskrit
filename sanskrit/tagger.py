"""
    sanskrit.tagger
    ~~~~~~~~~~~~~~~
    Code for converting Sanskrit paragraphs into a list of linguistic
    forms. This is done through a *part-of-speech tagger*
    (:class:`~sanskrit.tagger.Tagger`) that also removes sandhi and
    identifies the lexical roots that underlie the forms in some passage.

    When tagging, a block of text (i.e. a verse or paragraph) is called
    a *segment* and its space-separated substrings are called *chunks*.
    For example, the segment ``'aTa SabdAnuSAsanam |'`` has chunks
    ``'aTa'``, ``'SabdAnuSAsanam'``, and ``'|'``.

    :license: MIT

"""
from sanskrit import analyze, sandhi, schema


class NonForm:

    """Wraps a chunk that couldn't be parsed by the :class:`Tagger`."""

    def __init__(self, name):
        self.name = name


class TaggedItem:

    """Associates a linguistic form with a specific chunk and segment."""

    def __init__(self, segment_id, chunk_index, form):
        self.segment_id = segment_id
        self.chunk_index = chunk_index
        self.form = form

    def _enum_string(self, ctx, fields):
        strings = []
        enums = ctx.enum_abbr
        for field in fields:
            id = getattr(self.form, field + '_id')
            if id is not None:
                strings.append(enums[field][id])
            else:
                strings.append('')
        return '-'.join(strings)

    def human_readable_form(self, ctx):
        form = self.form
        if isinstance(form, NonForm):
            return (form.name, '', '', '')
        elif isinstance(form, schema.Indeclinable):
            return (form.name, 'indeclinable', '', '')
        elif isinstance(form, schema.Verb):
            return (form.name, 'verb', form.root.name,
                     self._enum_string(ctx,
                                       ['vclass', 'person', 'number', 'mode',
                                        'voice']))
        elif isinstance(form, schema.Nominal):
            return (form.name, 'nominal', form.stem.name,
                     self._enum_string(ctx, ['gender', 'case', 'number']))
        elif isinstance(form, schema.Infinitive):
            return (form.name, 'infinitive', form.root.name, '')
        elif isinstance(form, schema.Gerund):
            return (form.name, 'gerund', form.root.name, '')
        elif isinstance(form, schema.PerfectIndeclinable):
            return (form.name, 'perfect-indeclinable', form.root.name, '')


class Tagger:

    """The part-of-speech tagger."""

    def __init__(self, ctx):
        rules = [(x.first, x.second, x.result)
                 for x in ctx.session.query(schema.SandhiRule).all()]

        self.ctx = ctx
        self.splitter = sandhi.Splitter(rules)
        self.analyzer = analyze.SimpleAnalyzer(ctx)

    def iter_chunks(self, segment):
        """Iterate over the chunks in `segment`.

        :param segment: an arbitrary string
        """
        for line in segment.splitlines():
            for chunk in line.split():
                yield chunk

    def tag(self, segment, segment_id=None):
        """Return the linguistic forms that compose `segment`. If a form
        can't be parsed, it's wrapped in :class:`NonForm`.

        :param segment: an arbitrary string
        :return: a list of :class:`TaggedItem` objects.
        """
        for chunk_id, chunk in enumerate(self.iter_chunks(segment)):
            stack = [([], chunk)]
            while stack:
                done, remainder = stack.pop()
                if not remainder:
                    break

                for before, after in self.splitter.iter_splits(remainder):
                    for result in self.analyzer.analyze(before):
                        stack.append((done + [result], after))

            for item in done:
                yield TaggedItem(segment_id, chunk_id, item)
            if not done:
                yield TaggedItem(segment_id, chunk_id, NonForm(chunk))
