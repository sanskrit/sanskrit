from . import analyze, sandhi
from .schema import SandhiRule


class Tagger:

    def __init__(self, ctx):
        rules = [(x.first, x.second, x.result)
                 for x in ctx.session.query(SandhiRule).all()]

        self.ctx = ctx
        self.splitter = sandhi.Splitter(rules)
        self.analyzer = analyze.SimpleAnalyzer(ctx)

    def iter_chunks(self, blob):
        for line in blob.splitlines():
            for chunk in line.split():
                yield chunk

    def tag(self, blob):
        """

        :param blob: some blob of input text
        """
        for chunk in self.iter_chunks(blob):
            stack = [([], chunk)]
            while stack:
                done, remainder = stack.pop()
                if not remainder:
                    break

                for before, after in self.splitter.iter_splits(remainder):
                    for result in self.analyzer.analyze(before):
                        stack.append((done + [result], after))

            for item in done:
                yield item
            if not done:
                yield chunk
