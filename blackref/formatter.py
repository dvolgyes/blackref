#!/usr/bin/env python3
"""BibTeX formatting and processing functions."""

import bibtexparser
from .field_validators import (
    remove_empty_keys,
    fix_authors,
    fix_abstract,
    fix_isbn,
    fix_issn,
    fix_pages,
)
from .text_utils import fix_wrap


class LazyOpen:
    """Context manager for lazy file opening."""

    def __init__(self, s, mode: str):
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


def formatter(
    bib: bibtexparser.bibdatabase.BibDatabase,
    display_order: tuple,
    sort_fields: tuple,
    utf8_fields: set,
    latex_fields: set,
) -> str:
    """Format BibTeX database with specified options."""
    writer = bibtexparser.bwriter.BibTexWriter()
    writer.add_trailing_comma = True
    writer.display_order = display_order
    writer.order_entries_by = None
    writer.indent = " "
    writer.contents = ["preambles", "entries", "strings"]

    max_key_length = 10  # Minimum alignment
    for entry in bib.entries:
        entry = remove_empty_keys(entry)
        entry = fix_authors(entry, utf8_fields, latex_fields)
        entry = fix_abstract(entry, utf8_fields, latex_fields)
        entry = fix_isbn(entry)
        entry = fix_issn(entry)
        entry = fix_pages(entry)
        for key in entry.keys():
            max_key_length = max(max_key_length, len(key) + len(writer.indent) + 4)

    # Set align_values to the calculated maximum key length (minimum 10)
    writer.align_values = max_key_length

    for entry in bib.entries:
        for key in entry.keys():
            entry[key] = fix_wrap(entry[key], key, indent=max_key_length)

    for skey in reversed(sort_fields):
        reverse = skey[-1] == "-"
        if reverse:
            skey = skey[:-1]
        bib.entries = sorted(
            bib.entries, key=lambda x: x.get(skey, "").lower(), reverse=reverse
        )

    return writer.write(bib)
