#!/usr/bin/env python3
import argparse
import bibtexparser
import textwrap
import sys
from pathlib import Path
import isbnlib
import re

__version__ = '0.1.4'
__author__ = 'David Völgyes'
__email__ = 'david.volgyes@ieee.org'
__license__ = 'AGPLv3'
__summary__ = 'An uncompromising BibTeX/BibLaTeX reference list formatter.'
__description__ = __summary__


def fix_wrap(text, key, indent=10, line_length=80, relax=10):
    text = (
        text.replace("\n", " ").replace("\r", " ").replace(
            "\t", " ").replace("  ", " ")
    )
    wrapper = textwrap.TextWrapper()
    wrapper.width = line_length - indent
    wrapper.break_long_words = False
    wrapper.break_on_hyphen = False
    indent_text = " " * indent

    if (
        key.lower() in ["abstract", "title", "booktitle"]
        and len(text) > wrapper.width + relax
    ):
        N = len(text)
        if N < 2 * line_length:
            p = text[N // 2:].find(" ")
            if p >= 0:
                p += N // 2
                parts = [text[:p], text[p:]]
            else:
                parts = wrapper.wrap(text)
        else:
            parts = wrapper.wrap(text)
        result = f"\n{indent_text}".join(map(str.strip, parts))
        return result

    if key.lower() in ["author", "editor"]:
        names = text.strip().split(" and ")
        N = max(map(len, map(str.strip, names)))
        padded_names = []
        for name in names:
            k = N - len(name)
            padded_names.append(name + (" " * k))
        result = f"  and\n{indent_text}".join(padded_names).strip()
        return result

    if key.lower() in ["keywords", "keyword"]:
        keywords = text.strip().replace(';', ',').replace(', ', ',')
        keywords = keywords.replace(' ', '_').split(",")
        keywords = ", ".join(map(str.strip, keywords))
        parts = wrapper.wrap(keywords)
        result = f"\n{indent_text}".join(map(str.strip, parts))
        return result.replace('_', ' ')

    return text.strip()


def fix_isbn(entry):
    if 'isbn' in entry:
        value = entry['isbn']
        if isbnlib.is_isbn10(value):
            value = isbnlib.to_isbn13(value)
        if not isbnlib.is_isbn13(value):
            raise Exception(f'invalid isbn in {entry["ID"]}: {entry["isbn"]}')
        entry['isbn'] = isbnlib.mask(value, separator='-')
    return entry


def fix_issn(entry):
    if 'issn' in entry:
        value = entry['issn'].replace('-', '')
        value = value[0:4] + '-' + value[4:]
        if len(value) != 9:
            raise Exception(f'invalid issn in {entry["ID"]}: {entry["issn"]}')
        entry['issn'] = value
    return entry


def fix_pages(entry):
    if 'pages' in entry:
        value = entry['pages'].replace(' ', '')
        re.sub(r'([^-])-([^-])', r'r\g<1>--\g<2>', value)
        entry['pages'] = value
    return entry


def formatter(bib):
    writer = bibtexparser.bwriter.BibTexWriter()
    writer.add_trailing_comma = True
    writer.display_order = (
        "title",
        "booktitle",
        "author",
        "editor",
        "abstract",
        "journal",
        "issn",
        "year",
        "volume",
        "month",
        "number",
        "pages",
        "publisher",
        "address",
        "doi",
        "pubmedid",
        "url",
        "notes",
    )
    writer.ordering_entries_by = None
    writer.align_values = 10
    writer.indent = ' '
    writer.contents = ['preambles', 'entries', 'strings']

    bib.entries = sorted(bib.entries, key=lambda x: x["ID"].lower())

    max_key_length = 0
    for entry in bib.entries:
        for key in entry.keys():
            max_key_length = max(max_key_length, len(key)+len(writer.indent)+4)

    for entry in bib.entries:
        entry = fix_isbn(entry)
        entry = fix_pages(entry)
        for key in entry.keys():
            entry[key] = fix_wrap(entry[key], key, indent=max_key_length)
    return bibtexparser.dumps(bib, writer)


def main(cli_args=None):
    class lazy_open:
        def __init__(self, s, mode):
            self.s = s
            self.mode = mode
            self.fh = None

        def __enter__(self):
            if isinstance(self.s, str):
                self.fh = open(self.s, self.mode)
            else:
                self.fh = self.s
            return self.fh

        def __exit__(self, *exc):
            if isinstance(self.s, str):
                self.fh.close()
            return

    parser = argparse.ArgumentParser(
        description="The uncompromising reference formatter."
    )
    parser.add_argument(
        "-w", "--write-back", dest="writeback", action="store_true", default=False
    )
    parser.add_argument(
        "-u",
        "--utf8",
        dest="utf8",
        action="store_true",
        default=False,
        help="BibTeX cannot handle utf8, everything will be converted to LaTeX enconding by default. "
        "Biber and BibLaTeX are utf8 compatible.",
    )

    parser.add_argument(
        "-o",
        "--output",
        dest="output",
        metavar="DST",
        type=str,
        help="output file",
        default=sys.stdout,
    )
    parser.add_argument(
        "src", metavar="SRC", nargs="?", type=str, help="source file", default=sys.stdin
    )

    args = parser.parse_args(cli_args)
    if args.writeback:
        if args.output == sys.stdout and args.src != sys.stdin:
            args.output = args.src

    if args.src != sys.stdin and not Path(args.src).exists():
        eprint(f"Invalid input file: {args.src}")
        sys.exit(-1)

    with lazy_open(args.src, "rt") as fh:
        bib = bibtexparser.loads(fh.read())
        formatted = formatter(bib)
        print(formatted)

    # ~ if args.writeback or args.output:
        # ~ writer = bibtexparser.bwriter.BibTexWriter()
        # ~ writer.add_trailing_comma = True
        # ~ writer.display_order = (
        # ~ "title",
        # ~ "author",
        # ~ "booktitle",
        # ~ "editor",
        # ~ "abstract",
        # ~ "journal",
        # ~ "issn",
        # ~ "year",
        # ~ "volume",
        # ~ "month",
        # ~ "number",
        # ~ "pages",
        # ~ "publisher",
        # ~ "address",
        # ~ "doi",
        # ~ "pubmedid",
        # ~ "url",
        # ~ "notes",
        # ~ )
        # ~ writer.ordering_entries_by = None
        # ~ writer.align_values = 10
        # ~ writer.contents = ['preambles', 'entries','strings']

        # ~ if args.output is None:
        # ~ if args.writeback:
        # ~ args.output = args.src
        # ~ else:
        # ~ args.output = sys.stderr

        # ~ with lazy_open(args.output, "wt") as f:
        # ~ f.write(bibtexparser.dumps(bib, writer))
        # ~ pass
