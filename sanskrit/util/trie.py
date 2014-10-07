import collections


class HashTrie(object):

    """A fast trie, for short items."""

    def __init__(self):
        self.mapper = collections.defaultdict(set)
        self.len_longest = 0
        self.lengths = range(1, self.len_longest + 1)

    def __getitem__(self, key):
        return set.union(*[self.mapper[key[:i]] for i in self.lengths])

    def __setitem__(self, key, value):
        self.mapper[key].add(value)
        self.len_longest = max(len(key), self.len_longest)
        self.lengths = range(1, self.len_longest + 1)
