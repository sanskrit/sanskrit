from sanskrit import analyze, sandhi, schema


class TaggedItem:

    def __init__(self, segment_id, chunk_index, form):
        self.segment_id = segment_id
        self.chunk_index = chunk_index
        self.form = form

    def _enum_string(self, ctx, fields):
        strings = []
        enums = ctx.enum_abbr
        for field in fields:
            strings.append(enums[field][getattr(self.form, field + '_id')])
        return '-'.join(strings)

    def human_readable_form(self, ctx):
        form = self.form
        if isinstance(form, basestring):
            return (form, '', '', '')
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

    def __init__(self, ctx):
        rules = [(x.first, x.second, x.result)
                 for x in ctx.session.query(schema.SandhiRule).all()]

        self.ctx = ctx
        self.splitter = sandhi.Splitter(rules)
        self.analyzer = analyze.SimpleAnalyzer(ctx)

    def iter_chunks(self, blob):
        for line in blob.splitlines():
            for chunk in line.split():
                yield chunk

    def tag_segment(self, segment, segment_id=None):
        """

        :param segment: some blob of input text
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
                yield TaggedItem(segment_id, chunk_id, chunk)
