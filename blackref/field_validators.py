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


def fix_title_capitalization(entry: dict) -> dict:
    """Fix title field capitalization with warnings and brace protection."""
    return fix_field_capitalization(entry, "title")


def fix_booktitle_capitalization(entry: dict) -> dict:
    """Fix booktitle field capitalization with warnings and brace protection."""
    return fix_field_capitalization(entry, "booktitle")


def fix_publisher_capitalization(entry: dict) -> dict:
    """Fix publisher field capitalization with special rules for single words."""
    if "publisher" not in entry:
        return entry

    value = entry["publisher"].strip()
    if not value:
        return entry

    # Check if entire field is protected with double braces
    if value.startswith("{{") and value.endswith("}}"):
        logger.warning(
            f"Field 'publisher' in entry {entry.get('ID', 'unknown')} is entirely protected with braces: '{value}'"
        )
        return entry

    # Special rule for publisher: if single word and all caps, protect it
    words = value.split()
    if len(words) == 1:
        word = words[0]
        # Check if it's already protected with single braces
        if word.startswith("{") and word.endswith("}"):
            return entry  # Already protected, don't double-protect

        # Extract letters only for all-caps detection
        letter_chars = re.findall(r"[a-zA-Z]", word)
        if letter_chars and all(c.isupper() for c in letter_chars):
            # Single word, all caps - protect it
            entry["publisher"] = f"{{{word}}}"
            return entry

    # For multi-word publishers, use normal capitalization rules but skip all-caps warning
    # Check if everything is capitalized (excluding spaces and punctuation)
    letter_chars = re.findall(r"[a-zA-Z]", value)
    if letter_chars and all(c.isupper() for c in letter_chars) and len(words) > 1:
        logger.warning(
            f"Field 'publisher' in entry {entry.get('ID', 'unknown')} is entirely capitalized: '{value}'"
        )
        return entry

    # Apply normal mixed-case word protection
    entry["publisher"] = _protect_mixed_case_words(value)
    return entry


def fix_journal_capitalization(entry: dict) -> dict:
    """Fix journal field capitalization with special rules similar to publisher."""
    if "journal" not in entry:
        return entry

    value = entry["journal"].strip()
    if not value:
        return entry

    # Check if entire field is protected with double braces
    if value.startswith("{{") and value.endswith("}}"):
        logger.warning(
            f"Field 'journal' in entry {entry.get('ID', 'unknown')} is entirely protected with braces: '{value}'"
        )
        return entry

    # Check if it's already protected with single braces
    if value.startswith("{") and value.endswith("}"):
        return entry  # Already protected, don't double-protect

    # Check if everything is capitalized (excluding spaces and punctuation)
    letter_chars = re.findall(r"[a-zA-Z]", value)
    if letter_chars and all(c.isupper() for c in letter_chars):
        # All caps journal - protect the entire field
        entry["journal"] = f"{{{value}}}"
        return entry

    # Apply normal mixed-case word protection
    entry["journal"] = _protect_mixed_case_words(value)
    return entry


def fix_field_capitalization(entry: dict, field: str) -> dict:
    """Fix field capitalization with warnings and mixed-case word protection.

    Rules:
    1. Warn if everything is capitalized, then don't edit
    2. If entire field is protected with double braces {{...}}, remove outer braces and apply normal protection
    3. Otherwise, find single words with non-capital letters after first alphanumeric
       character and protect them with braces
    """
    if field not in entry:
        return entry

    value = entry[field].strip()
    if not value:
        return entry

    # Special handling for title and booktitle: if already wrapped in braces,
    # remove them and apply protection, then let writer add them back
    if (
        field in ["title", "booktitle"]
        and value.startswith("{")
        and value.endswith("}")
    ):
        # This could be from {{...}} in source (parsed to {...}) or {...} in source
        # Remove outer braces and apply normal mixed-case protection
        inner_content = value[1:-1]  # Remove { and }
        protected_content = _protect_mixed_case_words(inner_content)
        # Don't wrap in extra braces - let the BibTeX writer handle the outer braces
        entry[field] = protected_content
        return entry

    # Check if everything is capitalized (excluding spaces and punctuation)
    # Only consider letters for all-caps detection, not numbers
    letter_chars = re.findall(r"[a-zA-Z]", value)
    if letter_chars and all(c.isupper() for c in letter_chars):
        logger.warning(
            f"Field '{field}' in entry {entry.get('ID', 'unknown')} is entirely capitalized: '{value}'"
        )
        return entry

    # Check if entire field is protected with double braces (for non-title fields)
    if value.startswith("{{") and value.endswith("}}"):
        logger.warning(
            f"Field '{field}' in entry {entry.get('ID', 'unknown')} is entirely protected with braces: '{value}'"
        )
        return entry

    # Protect mixed-case words with braces
    entry[field] = _protect_mixed_case_words(value)
    return entry


def _protect_mixed_case_words(text: str) -> str:
    """Protect mixed-case words with braces, but skip already braced words.

    A word needs protection if it has uppercase letters after the first
    alphanumeric character (considering only alphanumeric characters).

    Examples:
    - 4D -> {4D}
    - IEEE -> {IEEE}
    - (IEEE) -> {(IEEE)}
    - GPUs -> {GPUs}
    - AutoMVQ -> {AutoMVQ}
    - Ok -> Ok (no protection needed)
    - {CNN} -> {CNN} (already protected, skip)
    """

    def should_protect_word(word: str) -> bool:
        """Check if a word needs brace protection."""
        # Skip if word is already protected with braces
        if word.startswith("{") and word.endswith("}"):
            return False

        # Extract alphanumeric characters only
        alphanumeric = re.findall(r"[a-zA-Z0-9]", word)
        if len(alphanumeric) < 2:
            return False

        # Check if there are uppercase letters after the first alphanumeric character
        return any(c.isupper() for c in alphanumeric[1:])

    def protect_word(word: str) -> str:
        """Wrap word in braces if it needs protection."""
        if should_protect_word(word):
            return f"{{{word}}}"
        return word

    # Handle edge case of whitespace-only text
    if not text.strip():
        return text

    # Split on whitespace and protect each word individually
    words = text.split()
    protected_words = [protect_word(word) for word in words]
    return " ".join(protected_words)
