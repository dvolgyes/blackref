#!/usr/bin/env python3
"""Field validation and fixing functions for BibTeX entries."""

import re
import isbnlib
from pylatexenc.latex2text import LatexNodes2Text
from pylatexenc.latexencode import unicode_to_latex
from loguru import logger


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
        # Remove all spaces and dashes first
        value = entry["issn"].replace("-", "").replace(" ", "")
        if len(value) != 8:
            raise Exception(f"invalid issn in {entry['ID']}: {entry['issn']}")
        # Format as XXXX-XXXX
        value = value[0:4] + "-" + value[4:]
        entry["issn"] = value
    return entry


def fix_pages(entry: dict) -> dict:
    """Fix page number format and normalize 'page' field to 'pages'."""
    # Handle 'page' field conversion to 'pages'
    if "page" in entry:
        if "pages" not in entry:
            entry["pages"] = entry["page"]
        entry.pop("page")

    if "pages" in entry:
        value = entry["pages"].replace(" ", "")
        # Convert various dash types to LaTeX emdash (--)
        # Handle en-dash (–), em-dash (—), and regular hyphen (-)
        value = value.replace("–", "--")  # en-dash to emdash
        value = value.replace("—", "--")  # em-dash to emdash
        # Convert single hyphens between non-dash characters to double dashes
        # This handles cases like "123-456" -> "123--456" but leaves "--" and "-" alone
        while re.search(r"([^-])-([^-])", value):
            value = re.sub(r"([^-])-([^-])", r"\g<1>--\g<2>", value)
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
        # Only apply LaTeX encoding if the text doesn't already contain LaTeX commands
        if not ("{\\" in value or "\\'" in value or "\\\\" in value):
            value = unicode_to_latex(value)
    entry[field] = value

    return entry


def fix_authors(entry: dict, utf8_fields: set, latex_fields: set) -> dict:
    """Fix author field encoding."""
    return fix_utf8_field(entry, "author", utf8_fields, latex_fields)


def fix_abstract(entry: dict, utf8_fields: set, latex_fields: set) -> dict:
    """Fix abstract field encoding."""
    return fix_utf8_field(entry, "abstract", utf8_fields, latex_fields)


def fix_unicode_dashes(entry: dict, field: str) -> dict:
    """Replace Unicode dashes with LaTeX equivalents in text fields.

    En-dash (–) becomes -- (double hyphen)
    Em-dash (—) becomes --- (triple hyphen)
    Regular hyphen (-) is preserved
    """
    if field not in entry:
        return entry

    value = entry[field]
    # Replace em-dash first (longer replacement)
    value = value.replace("—", "---")  # em-dash to triple hyphen
    value = value.replace("–", "--")  # en-dash to double hyphen
    entry[field] = value
    return entry


def fix_title_dashes(entry: dict) -> dict:
    """Fix Unicode dashes in title field."""
    return fix_unicode_dashes(entry, "title")


def fix_booktitle_dashes(entry: dict) -> dict:
    """Fix Unicode dashes in booktitle field."""
    return fix_unicode_dashes(entry, "booktitle")


def fix_abstract_dashes(entry: dict) -> dict:
    """Fix Unicode dashes in abstract field."""
    return fix_unicode_dashes(entry, "abstract")


def fix_doi(entry: dict) -> dict:
    """Fix DOI field by extracting from URL if needed.

    - If URL points to DOI (http[s]://[dx.]doi.org/{DOI}), extract {DOI}
    - If DOI and URL have same value (ignoring whitespace and case), remove URL
    - If DOI exists but doesn't have proper value: log error and don't change anything
    - If no DOI exists: create it with extracted {DOI} value
    - Remove URL item after successful DOI extraction or matching
    """
    if "url" not in entry:
        return entry

    url = entry["url"].strip()

    # Check if DOI and URL have exactly the same value (ignoring whitespace and case)
    if "doi" in entry:
        existing_doi = entry["doi"].strip()
        if existing_doi and existing_doi.lower() == url.lower():
            # DOI and URL are identical, remove URL
            entry.pop("url")
            return entry

    # Pattern to match DOI URLs: http[s]://[dx.]doi.org/{DOI}
    doi_url_pattern = r"^https?://(?:dx\.)?doi\.org/(.+)$"
    match = re.match(doi_url_pattern, url, re.IGNORECASE)

    if not match:
        return entry  # URL doesn't point to DOI

    extracted_doi = match.group(1)

    # Check if DOI field already exists
    if "doi" in entry:
        existing_doi = entry["doi"].strip()
        if existing_doi and existing_doi.lower() != extracted_doi.lower():
            logger.error(
                f"DOI mismatch in entry {entry.get('ID', 'unknown')}: existing='{existing_doi}' vs URL='{extracted_doi}'"
            )
            return entry  # Don't change anything on mismatch
        elif existing_doi:
            # DOI exists and matches (case insensitive), just remove URL and preserve existing DOI
            entry.pop("url")
            return entry

    # Set the DOI and remove URL
    entry["doi"] = extracted_doi
    entry.pop("url")

    return entry


def fix_month(entry: dict) -> dict:
    """Convert month names to numbers."""
    if "month" not in entry:
        return entry

    month_mapping = {
        "january": "1",
        "jan": "1",
        "february": "2",
        "feb": "2",
        "march": "3",
        "mar": "3",
        "april": "4",
        "apr": "4",
        "may": "5",
        "june": "6",
        "jun": "6",
        "july": "7",
        "jul": "7",
        "august": "8",
        "aug": "8",
        "september": "9",
        "sep": "9",
        "sept": "9",
        "october": "10",
        "oct": "10",
        "november": "11",
        "nov": "11",
        "december": "12",
        "dec": "12",
    }

    month_value = entry["month"].strip().lower()
    if month_value in month_mapping:
        entry["month"] = month_mapping[month_value]

    return entry
