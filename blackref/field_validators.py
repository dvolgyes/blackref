#!/usr/bin/env python3
"""Field validation and fixing functions for BibTeX entries."""

import re
import isbnlib
from pylatexenc.latex2text import LatexNodes2Text
from pylatexenc.latexencode import unicode_to_latex


def fix_isbn(entry: dict) -> dict:
    """Fix and validate ISBN format."""
    if "isbn" in entry:
        value = entry["isbn"]
        if isbnlib.is_isbn10(value):
            value = isbnlib.to_isbn13(value)
        if not isbnlib.is_isbn13(value):
            raise Exception(f"invalid isbn in {entry['ID']}: {entry['isbn']}")
        entry["isbn"] = isbnlib.mask(value, separator="-")
    return entry


def fix_issn(entry: dict) -> dict:
    """Fix and validate ISSN format."""
    if "issn" in entry:
        value = entry["issn"].replace("-", "")
        value = value[0:4] + "-" + value[4:]
        if len(value) != 9:
            raise Exception(f"invalid issn in {entry['ID']}: {entry['issn']}")
        entry["issn"] = value
    return entry


def fix_pages(entry: dict) -> dict:
    """Fix page number format."""
    if "pages" in entry:
        value = entry["pages"].replace(" ", "")
        re.sub(r"([^-])-([^-])", r"r\g<1>--\g<2>", value)
        entry["pages"] = value
    return entry


def remove_empty_keys(entry: dict) -> dict:
    """Remove empty or None fields from entry."""
    for key in list(entry.keys()):
        if entry[key] is None:
            entry[key] = ""
        v = str(entry[key]).strip()
        if len(v) == 0:
            entry.pop(key)
    return entry


def fix_utf8_field(
    entry: dict, field: str, utf8_fields: set, latex_fields: set
) -> dict:
    """Convert field between UTF-8 and LaTeX encoding."""
    if field not in entry:
        return entry

    value = entry[field]
    if field in utf8_fields:
        value = LatexNodes2Text().latex_to_text(value)
    elif field in latex_fields:
        value = unicode_to_latex(value)
    entry[field] = value

    return entry


def fix_authors(entry: dict, utf8_fields: set, latex_fields: set) -> dict:
    """Fix author field encoding."""
    return fix_utf8_field(entry, "author", utf8_fields, latex_fields)


def fix_abstract(entry: dict, utf8_fields: set, latex_fields: set) -> dict:
    """Fix abstract field encoding."""
    return fix_utf8_field(entry, "abstract", utf8_fields, latex_fields)
