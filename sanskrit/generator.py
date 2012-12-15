from . import util
from .schema import NominalEnding


class Generator(object):

    """A generator for various Sanskrit forms.

    Due to its inflectional nature, Sanskrit has tens of millions of
    different forms. It is not always feasible to store them in the
    database. But since the majority of the language is regular, we can
    store the principal parts of some group of forms and generate the
    whole group by applying some basic rules. That is, if we have 2000
    adjective stems and the 72 endings that they use, we can store 2072
    forms instead of 144k forms.

    :param context: some :class:`~sanskrit.Context`.
    """

    def __init__(self, context):
        self.ctx = ctx = context
        self.session = ctx.session_class()

        self.nominal_stem_trie = util.HashTrie()
        self.nominal_endings = {}
        seen = set()
        for e in self.session.query(NominalEnding):
            stem_type = e.stem_type
            if stem_type not in seen:
                seen.add(stem_type)
                self.nominal_stem_trie[stem_type[::-1]] = stem_type
                self.nominal_endings[stem_type] = {}

            key = (e.gender_id, e.case_id, e.number_id)
            self.nominal_endings[stem_type][key] = e.name

    def nominal_paradigm(self, stem_name, gender):
        """Generate a full paradigm using normal Sanskrit rules. The
        function treats irregular stems as regular.
        """

        stem_types = self.nominal_stem_trie[stem_name[::-1]]
        stem_type = max(stem_types, key=len)
        truncated = stem_name[:-len(stem_type)]
        endings = self.nominal_endings[stem_type]

        returned = {}
        enum = self.ctx.enum_id
        gender_id = enum['gender'][gender]
        for case in '12345678':
            case_id = enum['case'][case]
            for number in 'sdp':
                number_id = enum['number'][number]
                key = (gender_id, case_id, number_id)
                returned[(case, number)] = truncated + endings[key]

        return returned
