"""
    sanskrit.shell
    ~~~~~~~~~~~~~~

    A convenient REPL for fixing errors in the tagger output.

    :license: MIT
"""
from __future__ import print_function
from builtins import input
from builtins import range
from builtins import object
import re

from sanskrit import tagger


class Color(object):

    """Terminal colors. Unix systems only."""

    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'

    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    END = '\033[0m'


def with_color(s, colors):
    """Convenience function that adds `Color.END`."""
    return colors + s + Color.END


def print_with_highlighted_chunk(segment, n):
    """Returns a clean version of `segment` with chunk `n` in red."""
    chunks = [x.split() for x in segment.strip().splitlines()]
    i = 0
    for L, line in enumerate(chunks):
        for c, chunk in enumerate(line):
            if i == n:
                s = chunks[L][c]
                chunks[L][c] = with_color(s, Color.RED + Color.BOLD)
                print('\n'.join([' '.join(x) for x in chunks]))
                return
            else:
                i += 1


def print_numbered_items(items, ctx):
    """Convenience function to print a numbered list of items."""
    for i, item in enumerate(items):
        hrf = item.human_readable_form(ctx)
        pos = hrf[1]
        print('{} : {}'.format((i + 1), hrf))


def int_or_none(x, limit):
    """Returns `int(x)` if `x` is a valid `int` or `None` otherwise.

    `x` is valid if `1 <= x <= limit`.
    """
    try:
        value = int(x)
        if 1 <= value <= limit:
            return value
        else:
            return None
    except ValueError:
        return None


def print_help():
    print(with_color('1  : get alternatives for form 1', Color.GREEN))
    print(with_color('s  : re-split the chunk', Color.GREEN))
    print(with_color('pc : previous chunk', Color.GREEN))
    print(with_color('nc : next chunk', Color.GREEN))
    print(with_color('q  : quit', Color.GREEN))  # TODO: save and quit
    print(with_color('?  : help', Color.GREEN))


def segment_repl(ctx, segment):
    print(with_color('*' + '-' * 50, Color.GREEN + Color.BOLD))
    print(with_color('*', Color.GREEN + Color.BOLD))
    print(with_color('* Interactive Sanskrit tagger', Color.GREEN + Color.BOLD))
    print(with_color('*', Color.GREEN + Color.BOLD))
    print(with_color('*' + '-' * 50, Color.GREEN + Color.BOLD))
    print_help()

    t = tagger.Tagger(ctx)

    # Chunk index -> list of TaggedItems
    items_for_chunk = {}
    for item in t.tag(segment):
        items_for_chunk.setdefault(item.chunk_index, []).append(item)

    # Chunk index -> highlighted chunk
    index = 0
    chunks = list(t.iter_chunks(segment))
    n = len(chunks)

    while index < n:
        if re.match("^[0-9|./]+$", chunks[index]):
            index += 1
            continue

        print(with_color('~' * 50, Color.BLUE + Color.BOLD))
        print()
        print_with_highlighted_chunk(segment, index)
        print()
        print_numbered_items(items_for_chunk[index], ctx)
        print()

        command = input(": ")
        int_command = int_or_none(command, limit=len(items_for_chunk[index]))

        # All OK
        if not command or command == 'nc':
            index += 1

        elif command == '?' or command == 'help':
            print_help()

        # Go back one
        elif command == 'pc':
            if index > 0:
                index -= 1

        elif command == 'q':
            return

        # Bad split
        elif command == 's':
            split = input("Split: ")
            items_for_chunk[index] = list(t.tag_segment(split))

        # Bad form
        elif int_command is not None:
            bad_item = items_for_chunk[index][int_command - 1]
            candidate_items = []
            for form in t.analyzer.analyze(bad_item.form.name):
                candidate_items.append(
                    tagger.TaggedItem(bad_item.segment_id,
                                      bad_item.chunk_index, form))

            print_numbered_items(candidate_items, ctx)

            choice = None
            while choice is None:
                choice = int_or_none(input('Which? : '),
                                     limit=len(candidate_items))

            items_for_chunk[index][int_command - 1] = candidate_items[choice - 1]

        else:
            print()
            msg = "Unrecognized command '%s'. Try one of these:" % command
            print(with_color(msg, Color.BOLD + Color.GREEN))
            print_help()

    # All done!
    # TODO: write to file
    for i in range(n):
        for item in items_for_chunk[i]:
            print(item.human_readable_form(ctx))


def run(ctx, segment):
    segment_repl(ctx, segment)
