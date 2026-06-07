#!/usr/bin/env python3
"""BibTeX formatting and processing functions."""

from pathlib import Path
from types import TracebackType
from typing import IO, cast

import bibtexparser
from .field_validators import (
    remove_empty_keys,
    fix_html_entities,
    fix_authors,
    fix_abstract,
    fix_isbn,
    fix_issn,
    fix_pages,
    fix_month,
    fix_title_dashes,
    fix_booktitle_dashes,
    fix_abstract_dashes,
    fix_doi,
    fix_title_capitalization,
    fix_booktitle_capitalization,
    fix_publisher_capitalization,
    fix_journal_capitalization,
    fix_title_periods,
    fix_booktitle_periods,
    fix_publisher_periods,
    fix_journal_periods,
    fix_url_archiving,
)
from .text_utils import fix_wrap


class LazyOpen:
    """Context manager for lazy file opening."""

    def __init__(self, s: str | IO[str], mode: str) -> None:
        self.s = s
        self.mode = mode
        self.fh: IO[str] | None = None

    def __enter__(self) -> IO[str]:
        if isinstance(self.s, str):
            self.fh = Path(self.s).open(self.mode, encoding="utf-8")
        else:
            self.fh = self.s
        return self.fh

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if isinstance(self.s, str):
            if self.fh is None:
                return
            self.fh.close()


def formatter(
    bib: bibtexparser.bibdatabase.BibDatabase,
    display_order: tuple[str, ...],
    sort_fields: tuple[str, ...],
    utf8_fields: set[str],
    latex_fields: set[str],
    formatting_mode: str = "full",
    wayback: bool = False,
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
        processed_entry = entry
        if formatting_mode == "full":
            processed_entry = remove_empty_keys(processed_entry)
            processed_entry = fix_html_entities(processed_entry)
            processed_entry = fix_authors(processed_entry, utf8_fields, latex_fields)
            processed_entry = fix_abstract(processed_entry, utf8_fields, latex_fields)
            processed_entry = fix_isbn(processed_entry)
            processed_entry = fix_issn(processed_entry)
            processed_entry = fix_pages(processed_entry)
            processed_entry = fix_month(processed_entry)
            # Fix Unicode dashes in text fields
            processed_entry = fix_title_dashes(processed_entry)
            processed_entry = fix_booktitle_dashes(processed_entry)
            processed_entry = fix_abstract_dashes(processed_entry)
            # Fix DOI extraction from URLs
            processed_entry = fix_doi(processed_entry)
            # Fix capitalization and protect mixed-case words
            processed_entry = fix_title_capitalization(processed_entry)
            processed_entry = fix_booktitle_capitalization(processed_entry)
            processed_entry = fix_publisher_capitalization(processed_entry)
            processed_entry = fix_journal_capitalization(processed_entry)
            # Remove trailing periods from title fields
            processed_entry = fix_title_periods(processed_entry)
            processed_entry = fix_booktitle_periods(processed_entry)
            processed_entry = fix_publisher_periods(processed_entry)
            processed_entry = fix_journal_periods(processed_entry)
            # Archive URLs and add urldate (only if wayback flag is enabled)
            if wayback:
                processed_entry = fix_url_archiving(processed_entry)
        for key in processed_entry:
            max_key_length = max(max_key_length, len(key) + len(writer.indent) + 4)

    # Set align_values to the calculated maximum key length (minimum 10)
    writer.align_values = max_key_length

    for entry in bib.entries:
        for key in entry:
            if formatting_mode == "full":
                entry[key] = fix_wrap(entry[key], key, indent=max_key_length)
            else:
                # In basic mode, only apply basic text normalization
                entry[key] = " ".join(str(entry[key]).split())

    for sort_key in reversed(sort_fields):
        reverse = sort_key[-1] == "-"
        active_sort_key = sort_key
        if reverse:
            active_sort_key = sort_key[:-1]
        bib.entries = sorted(
            bib.entries,
            key=lambda x: x.get(active_sort_key, "").lower(),
            reverse=reverse,
        )

    return cast(str, writer.write(bib))
