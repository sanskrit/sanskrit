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
from sanskrit import analyze, sandhi, schema, util


class NonForm:

    """Wraps a chunk that couldn't be parsed by the :class:`Tagger`."""

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "NonForm('{}')".format(self.name)


class Model:

    """A statistical model used to calculate conditional probabilities."""

    def __init__(self):
        pass

    def log_cond_prob(self, before, cur):
        """Return the log probability of `cur` given the items in `before`

        :param before: a list of :class:`TaggedItem` objects.
        :param cur: the most recent :class:`TaggedItem`
        """
        # TODO: non-heuristic solution
        if isinstance(cur, NonForm):
            return -1
        else:
            return len(cur.name)


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
        self.model = Model()

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
        chunks = list(self.iter_chunks(segment))
        if not chunks:
            return

        q = util.PriorityQueue()
        q.push(([], 0, chunks[0]), 0)

        done = []
        while q:
            (done, chunk_index, remainder), priority = q.pop_with_priority()
            # Chunk is done
            if not remainder:
                if chunk_index + 1 < len(chunks):
                    new_state = (done, chunk_index + 1, chunks[chunk_index + 1])
                    q.push(new_state, priority)
                    continue
                else:
                    # Segment is done!
                    break

            for before, after in self.splitter.iter_splits(remainder):
                # Without this line, the tagger could loop forever. This
                # looping occurs if a sandhi rule has the form "X -> Y X",
                # which yields Y while leaving the term with X unchanged.
                if remainder == after: continue

                for result in self.analyzer.analyze(before):
                    item = TaggedItem(segment_id, chunk_index, result)
                    q.push((done + [item], chunk_index, after),
                            priority + self.model.log_cond_prob(done, result))

            # Add "default" state in case nothing could be found.
            if remainder == chunks[chunk_index]:
                result = NonForm(remainder)
                item = TaggedItem(segment_id, chunk_index, result)
                new_state = (done + [item], chunk_index, None)
                q.push(new_state, priority +
                       self.model.log_cond_prob(done, result))

        return done
