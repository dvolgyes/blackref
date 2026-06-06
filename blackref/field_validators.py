#!/usr/bin/env python3
"""Field validation and fixing functions for BibTeX entries."""

# ruff: noqa: RUF001, RUF002, RUF003

import html
import re
from datetime import datetime

import httpx2
import isbnlib
from loguru import logger
from pylatexenc.latex2text import LatexNodes2Text
from pylatexenc.latexencode import unicode_to_latex

BibEntry = dict[str, str]


def fix_html_entities(entry: BibEntry) -> BibEntry:
    """Convert HTML entities to appropriate LaTeX or UTF-8 equivalents in all text fields."""
    text_fields = [
        "title",
        "booktitle",
        "journal",
        "author",
        "editor",
        "publisher",
        "address",
        "organization",
        "school",
        "institution",
        "note",
        "notes",
        "abstract",
        "keywords",
        "series",
        "chapter",
        "edition",
    ]

    # Fields where mathematical symbols and arrows are typically inappropriate
    title_like_fields = ["title", "booktitle", "journal"]

    for field in text_fields:
        if field in entry:
            original_text = entry[field]
            converted_text = _convert_html_entities(original_text)

            # Check for potentially inappropriate symbols in title-like fields
            if field in title_like_fields:
                _check_for_inappropriate_symbols(
                    converted_text, field, entry.get("ID", "unknown")
                )

            entry[field] = converted_text

    return entry


def _convert_html_entities(text: str) -> str:
    """Convert HTML entities to LaTeX or UTF-8 equivalents.

    Strategy:
    1. Basic entities: &amp; &lt; &gt; -> LaTeX equivalents
    2. Quotes: Various quote entities -> LaTeX quotes (``, '', etc.)
    3. Typography: &ndash; &mdash; &hellip; -> LaTeX equivalents
    4. Spacing: &nbsp; -> regular space
    5. Accented characters: Convert to UTF-8 (é, ø, æ, etc.)
    6. Mathematical symbols: -> LaTeX equivalents
    7. Greek letters: -> LaTeX equivalents
    8. General entities: Use html.unescape() as fallback
    """
    if not text or "&" not in text:
        return text

    # Define comprehensive entity mappings
    entity_mappings = {
        # Basic HTML entities -> LaTeX
        "&amp;": "&",  # Let BibTeX handle ampersand naturally
        "&lt;": r"<",  # Keep as-is for BibTeX
        "&gt;": r">",  # Keep as-is for BibTeX
        # Quotation marks -> LaTeX quotes
        "&quot;": "''",  # Generic double quote -> LaTeX closing double quote
        "&apos;": "'",  # Apostrophe -> single quote
        "&lsquo;": "`",  # Left single quote -> LaTeX opening single quote
        "&rsquo;": "'",  # Right single quote -> LaTeX closing single quote
        "&ldquo;": "``",  # Left double quote -> LaTeX opening double quote
        "&rdquo;": "''",  # Right double quote -> LaTeX closing double quote
        "&laquo;": r"\guillemotleft",  # Left double angle quote
        "&raquo;": r"\guillemotright",  # Right double angle quote
        "&bdquo;": ",,",  # German double low-9 quote
        "&sbquo;": ",",  # German single low-9 quote
        # Typography
        "&ndash;": "--",  # En dash -> LaTeX en dash
        "&mdash;": "---",  # Em dash -> LaTeX em dash
        "&hellip;": r"\ldots",  # Horizontal ellipsis -> LaTeX
        "&nbsp;": " ",  # Non-breaking space -> regular space
        # Mathematical symbols - use text-mode or UTF-8
        "&deg;": r"${}^\circ$",  # Keep this one as it's commonly used
        "&plusmn;": "±",  # UTF-8 plus-minus
        "&times;": "×",  # UTF-8 multiplication
        "&divide;": "÷",  # UTF-8 division
        "&frac12;": "½",  # UTF-8 one half
        "&frac14;": "¼",  # UTF-8 one quarter
        "&frac34;": "¾",  # UTF-8 three quarters
        "&sup1;": "¹",  # UTF-8 superscript 1
        "&sup2;": "²",  # UTF-8 superscript 2
        "&sup3;": "³",  # UTF-8 superscript 3
        "&micro;": "µ",  # UTF-8 micro sign
        "&infin;": "∞",  # UTF-8 infinity
        # Arrows - use UTF-8
        "&larr;": "←",  # Left arrow
        "&rarr;": "→",  # Right arrow
        "&uarr;": "↑",  # Up arrow
        "&darr;": "↓",  # Down arrow
        "&harr;": "↔",  # Left-right arrow
        "&lArr;": "⇐",  # Double left arrow
        "&rArr;": "⇒",  # Double right arrow
        "&uArr;": "⇑",  # Double up arrow
        "&dArr;": "⇓",  # Double down arrow
        "&hArr;": "⇔",  # Double left-right arrow
        # Symbols - text-mode commands
        "&copy;": r"\copyright",
        "&reg;": r"\textregistered",
        "&trade;": r"\texttrademark",
        "&sect;": r"\S",
        "&para;": r"\P",
        "&dagger;": r"\textdagger",
        "&Dagger;": r"\textdaggerdbl",
        "&bull;": r"\textbullet",
        # Greek letters (lowercase) - use UTF-8
        "&alpha;": "α",
        "&beta;": "β",
        "&gamma;": "γ",
        "&delta;": "δ",
        "&epsilon;": "ε",
        "&zeta;": "ζ",
        "&eta;": "η",
        "&theta;": "θ",
        "&iota;": "ι",
        "&kappa;": "κ",
        "&lambda;": "λ",
        "&mu;": "μ",
        "&nu;": "ν",
        "&xi;": "ξ",
        "&omicron;": "ο",
        "&pi;": "π",
        "&rho;": "ρ",
        "&sigma;": "σ",
        "&tau;": "τ",
        "&upsilon;": "υ",
        "&phi;": "φ",
        "&chi;": "χ",
        "&psi;": "ψ",
        "&omega;": "ω",
        # Greek letters (uppercase) - use UTF-8
        "&Alpha;": "Α",
        "&Beta;": "Β",
        "&Gamma;": "Γ",
        "&Delta;": "Δ",
        "&Epsilon;": "Ε",
        "&Zeta;": "Ζ",
        "&Eta;": "Η",
        "&Theta;": "Θ",
        "&Iota;": "Ι",
        "&Kappa;": "Κ",
        "&Lambda;": "Λ",
        "&Mu;": "Μ",
        "&Nu;": "Ν",
        "&Xi;": "Ξ",
        "&Omicron;": "Ο",
        "&Pi;": "Π",
        "&Rho;": "Ρ",
        "&Sigma;": "Σ",
        "&Tau;": "Τ",
        "&Upsilon;": "Υ",
        "&Phi;": "Φ",
        "&Chi;": "Χ",
        "&Psi;": "Ψ",
        "&Omega;": "Ω",
    }

    # Apply manual mappings first
    for entity, replacement in entity_mappings.items():
        text = text.replace(entity, replacement)

    # Check for any remaining unconverted HTML entities
    remaining_entities = re.findall(r"&[a-zA-Z][a-zA-Z0-9]*;", text)
    if remaining_entities:
        logger.warning(f"Found unconverted HTML entities: {remaining_entities}")

    # For remaining entities (especially accented characters), use html.unescape
    # to convert to UTF-8, which is what we want for European characters
    text = html.unescape(text)

    # Final step: escape any remaining bare ampersands for LaTeX
    # Only escape & that are not already escaped (i.e., not preceded by backslash)
    return re.sub(r"(?<!\\)&", r"\\&", text)


def _check_for_inappropriate_symbols(text: str, field: str, entry_id: str) -> None:
    """Check for mathematical symbols and arrows that might be inappropriate in titles."""
    # Mathematical symbols that are often inappropriate in titles
    math_symbols = [
        "±",
        "×",
        "÷",
        "µ",
        "∞",
        "½",
        "¼",
        "¾",
        "¹",
        "²",
        "³",
        "${}^\\circ$",
        "°",  # degree symbols
    ]

    # Arrow symbols that are often inappropriate in titles
    arrow_symbols = ["←", "→", "↑", "↓", "↔", "⇐", "⇒", "⇑", "⇓", "⇔"]

    # Greek letters that might be inappropriate in titles (except common ones)
    greek_symbols = [
        "α",
        "β",
        "γ",
        "δ",
        "ε",
        "ζ",
        "η",
        "θ",
        "ι",
        "κ",
        "λ",
        "μ",
        "ν",
        "ξ",
        "ο",
        "π",
        "ρ",
        "σ",
        "τ",
        "υ",
        "φ",
        "χ",
        "ψ",
        "ω",
        "Α",
        "Β",
        "Γ",
        "Δ",
        "Ε",
        "Ζ",
        "Η",
        "Θ",
        "Ι",
        "Κ",
        "Λ",
        "Μ",
        "Ν",
        "Ξ",
        "Ο",
        "Π",
        "Ρ",
        "Σ",
        "Τ",
        "Υ",
        "Φ",
        "Χ",
        "Ψ",
        "Ω",
    ]

    found_symbols = []

    # Check for mathematical symbols
    for symbol in math_symbols:
        if symbol in text:
            found_symbols.append(f"math symbol '{symbol}'")

    # Check for arrows
    for symbol in arrow_symbols:
        if symbol in text:
            found_symbols.append(f"arrow '{symbol}'")

    # Check for Greek letters (but be less strict - only warn if many are found)
    greek_found = [symbol for symbol in greek_symbols if symbol in text]
    if len(greek_found) >= 2:  # Only warn if multiple Greek letters found
        found_symbols.append(f"Greek letters {greek_found}")

    if found_symbols:
        logger.warning(
            f"Entry '{entry_id}' field '{field}' contains potentially inappropriate symbols: "
            f"{', '.join(found_symbols)}. Consider if these belong in a {field}."
        )


def fix_isbn(entry: BibEntry) -> BibEntry:
    """Fix and validate ISBN format."""
    if "isbn" in entry:
        value = entry["isbn"]
        if isbnlib.is_isbn10(value):
            value = isbnlib.to_isbn13(value)
        if not isbnlib.is_isbn13(value):
            raise Exception(f"invalid isbn in {entry['ID']}: {entry['isbn']}")
        entry["isbn"] = isbnlib.mask(value, separator="-")
    return entry


def fix_issn(entry: BibEntry) -> BibEntry:
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


def fix_pages(entry: BibEntry) -> BibEntry:
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


def remove_empty_keys(entry: BibEntry) -> BibEntry:
    """Remove empty or None fields from entry."""
    for key in list(entry.keys()):
        if entry[key] is None:
            entry[key] = ""
        v = str(entry[key]).strip()
        if len(v) == 0:
            entry.pop(key)
    return entry


def fix_utf8_field(
    entry: BibEntry, field: str, utf8_fields: set[str], latex_fields: set[str]
) -> BibEntry:
    """Convert field between UTF-8 and LaTeX encoding."""
    if field not in entry:
        return entry

    value = entry[field]
    if field in utf8_fields:
        value = LatexNodes2Text().latex_to_text(value)
    elif field in latex_fields:
        # Only apply LaTeX encoding if the text doesn't already contain LaTeX commands
        # Check for various LaTeX command patterns
        has_latex_commands = (
            "{\\" in value  # Braced commands like {\LaTeX}
            or "\\'" in value  # Accented characters like \'e
            or "\\\\" in value  # Double backslashes
            or "\\&" in value  # Escaped ampersands
            or "\\$" in value  # Escaped dollars
            or "\\%" in value  # Escaped percent
            or "\\#" in value  # Escaped hash
            or "\\_" in value  # Escaped underscores
            or "\\{" in value  # Escaped braces
            or "\\}" in value  # Escaped braces
            or "\\textbackslash" in value  # Already encoded backslashes
        )
        if not has_latex_commands:
            value = unicode_to_latex(value)
    entry[field] = value

    return entry


def fix_authors(
    entry: BibEntry, utf8_fields: set[str], latex_fields: set[str]
) -> BibEntry:
    """Fix author field encoding and replace & variants with 'and'."""
    if "author" in entry:
        # Replace & variants with proper BibTeX 'and' separator
        entry["author"] = (
            entry["author"]
            .replace("&amp;", " and ")
            .replace("\\&", " and ")
            .replace("&", " and ")
        )
        # Clean up multiple spaces
        entry["author"] = " ".join(entry["author"].split())

    return fix_utf8_field(entry, "author", utf8_fields, latex_fields)


def fix_abstract(
    entry: BibEntry, utf8_fields: set[str], latex_fields: set[str]
) -> BibEntry:
    """Fix abstract field encoding."""
    return fix_utf8_field(entry, "abstract", utf8_fields, latex_fields)


def fix_unicode_dashes(entry: BibEntry, field: str) -> BibEntry:
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


def fix_title_dashes(entry: BibEntry) -> BibEntry:
    """Fix Unicode dashes in title field."""
    return fix_unicode_dashes(entry, "title")


def fix_booktitle_dashes(entry: BibEntry) -> BibEntry:
    """Fix Unicode dashes in booktitle field."""
    return fix_unicode_dashes(entry, "booktitle")


def fix_abstract_dashes(entry: BibEntry) -> BibEntry:
    """Fix Unicode dashes in abstract field."""
    return fix_unicode_dashes(entry, "abstract")


def fix_doi(entry: BibEntry) -> BibEntry:
    """Fix DOI field by extracting from URL if needed.

    - If URL points to DOI (http[s]://[dx.]doi.org/{DOI}), extract {DOI}
    - If URL points to arXiv (https://arxiv.org/abs/{ID} or https://arxiv.org/pdf/{ID}), create DOI 10.48550/arXiv.{ID}
    - If DOI and URL have same value (ignoring whitespace and case), remove URL
    - If DOI exists but doesn't have proper value: log error and don't change anything
    - If no DOI exists: create it with extracted {DOI} value
    - Remove URL item after successful DOI extraction or matching
    - Fix arXiv DOI formatting to use proper capitalization (10.48550/arXiv.)
    """
    if "url" not in entry:
        # Check if we have an existing DOI that needs case fixing for arXiv
        if "doi" in entry:
            existing_doi = entry["doi"].strip()
            if existing_doi and "arxiv" in existing_doi.lower():
                # Fix arXiv DOI capitalization
                entry["doi"] = _fix_arxiv_doi_case(existing_doi)
        return entry

    url = entry["url"].strip()

    # Check if DOI and URL have exactly the same value (ignoring whitespace and case)
    if "doi" in entry:
        existing_doi = entry["doi"].strip()
        if existing_doi and existing_doi.lower() == url.lower():
            # DOI and URL are identical, remove URL
            entry.pop("url")
            return entry

    # Pattern to match arXiv URLs: https://arxiv.org/abs/{ID} or https://arxiv.org/pdf/{ID}
    arxiv_url_pattern = r"^https?://arxiv\.org/(?:abs|pdf)/(.+?)(?:\.pdf)?$"
    arxiv_match = re.match(arxiv_url_pattern, url, re.IGNORECASE)

    if arxiv_match:
        arxiv_id = arxiv_match.group(1)
        arxiv_doi = f"10.48550/arXiv.{arxiv_id}"

        # Check if DOI field already exists
        if "doi" in entry:
            existing_doi = entry["doi"].strip()
            if existing_doi:
                # Fix case of existing arXiv DOI
                existing_doi_fixed = _fix_arxiv_doi_case(existing_doi)
                if existing_doi_fixed.lower() != arxiv_doi.lower():
                    logger.error(
                        f"DOI mismatch in entry {entry.get('ID', 'unknown')}: existing='{existing_doi}' vs arXiv URL='{arxiv_doi}'"
                    )
                    return entry  # Don't change anything on mismatch
                # DOI exists and matches (case insensitive), just remove URL and fix DOI case
                entry["doi"] = existing_doi_fixed
                entry.pop("url")
                return entry

        # Set the arXiv DOI and remove URL
        entry["doi"] = arxiv_doi
        entry.pop("url")
        return entry

    # Pattern to match DOI URLs: http[s]://[dx.]doi.org/{DOI}
    doi_url_pattern = r"^https?://(?:dx\.)?doi\.org/(.+)$"
    match = re.match(doi_url_pattern, url, re.IGNORECASE)

    if not match:
        return entry  # URL doesn't point to DOI or arXiv

    extracted_doi = match.group(1)

    # Check if DOI field already exists
    if "doi" in entry:
        existing_doi = entry["doi"].strip()
        if existing_doi and existing_doi.lower() != extracted_doi.lower():
            logger.error(
                f"DOI mismatch in entry {entry.get('ID', 'unknown')}: existing='{existing_doi}' vs URL='{extracted_doi}'"
            )
            return entry  # Don't change anything on mismatch
        if existing_doi:
            # DOI exists and matches (case insensitive), just remove URL and preserve existing DOI
            entry.pop("url")
            return entry

    # Set the DOI and remove URL
    entry["doi"] = extracted_doi
    entry.pop("url")

    return entry


def _fix_arxiv_doi_case(doi: str) -> str:
    """Fix arXiv DOI capitalization to use proper format 10.48550/arXiv.{ID}"""
    # Pattern to match arXiv DOIs with case variations
    arxiv_doi_pattern = r"^(10\.48550/)(arxiv\.?)(.+)$"
    match = re.match(arxiv_doi_pattern, doi, re.IGNORECASE)

    if match:
        prefix = match.group(1)  # "10.48550/"
        arxiv_id = match.group(3)  # ID part
        return f"{prefix}arXiv.{arxiv_id}"

    return doi  # Return unchanged if not an arXiv DOI


def fix_month(entry: BibEntry) -> BibEntry:
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


def fix_title_capitalization(entry: BibEntry) -> BibEntry:
    """Fix title field capitalization with warnings and brace protection."""
    return fix_field_capitalization(entry, "title")


def fix_booktitle_capitalization(entry: BibEntry) -> BibEntry:
    """Fix booktitle field capitalization with warnings and brace protection."""
    return fix_field_capitalization(entry, "booktitle")


def fix_publisher_capitalization(entry: BibEntry) -> BibEntry:
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


def fix_journal_capitalization(entry: BibEntry) -> BibEntry:
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
        # Check if it's multi-word - if so, warn and don't edit
        words = value.split()
        if len(words) > 1:
            logger.warning(
                f"Field 'journal' in entry {entry.get('ID', 'unknown')} is entirely capitalized (multi-word): '{value}'"
            )
            return entry
        # Single word all caps journal - protect the entire field
        entry["journal"] = f"{{{value}}}"
        return entry

    # Apply normal mixed-case word protection
    entry["journal"] = _protect_mixed_case_words(value)
    return entry


def _has_matching_outer_braces(text: str) -> bool:
    """Check if text has matching outer braces that wrap the entire content.

    Returns True only if the first { and last } form a matching pair that
    encompasses the entire text content.

    Examples:
    - "{content}" -> True
    - "{CPUs} and {GPUs}" -> True (outer braces wrap everything)
    - "{CPUs} {GPUs}" -> False (first { and last } are from different words)
    """
    if not (text.startswith("{") and text.endswith("}")):
        return False

    # Track brace depth to see if first and last braces match
    depth = 0
    for i, char in enumerate(text):
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            # If we hit depth 0 before the last character, the first and last braces don't match
            if depth == 0 and i < len(text) - 1:
                return False

    return depth == 0


def fix_field_capitalization(entry: BibEntry, field: str) -> BibEntry:
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

    # Special handling for title and booktitle: if already wrapped in matching outer braces,
    # check if it came from double braces and handle appropriately
    if field in ["title", "booktitle"] and _has_matching_outer_braces(value):
        # This could be from {{...}} in source (parsed to {...}) or {...} in source
        inner_content = value[1:-1]  # Remove outer { and }

        # Check if this looks like it came from {{...}} source with mixed brace structure
        # Indicators: starts/ends with unmatched braces, or has complex brace patterns
        if (
            inner_content.startswith("}")
            or inner_content.endswith("{")
            or ":}" in inner_content
            or "{:" in inner_content
        ):
            # This likely came from {{...}} source with intentional mixed brace structure
            # Preserve as-is since this was intentionally double-braced
            return entry

        # Apply normal mixed-case protection to inner content
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


def remove_trailing_period(entry: BibEntry, field: str) -> BibEntry:
    """Remove trailing period from field while preserving protecting braces.

    Handles cases like:
    - "Title." -> "Title"
    - "Title.}" -> "Title}"
    - "{Title.}" -> "{Title}"
    - "Title with {LaTeX}." -> "Title with {LaTeX}"
    """
    if field not in entry:
        return entry

    value = entry[field].strip()
    if not value:
        return entry

    # Check if ends with period or period followed by closing brace
    if value.endswith("."):
        # Remove trailing period
        entry[field] = value[:-1]
    elif value.endswith(".}"):
        # Remove period but keep closing brace
        entry[field] = value[:-2] + "}"

    return entry


def fix_title_periods(entry: BibEntry) -> BibEntry:
    """Remove trailing periods from title field."""
    return remove_trailing_period(entry, "title")


def fix_booktitle_periods(entry: BibEntry) -> BibEntry:
    """Remove trailing periods from booktitle field."""
    return remove_trailing_period(entry, "booktitle")


def fix_publisher_periods(entry: BibEntry) -> BibEntry:
    """Remove trailing periods from publisher field, but preserve abbreviations.

    Preserves periods after words of 4 characters or less (likely abbreviations
    like Inc., Ltd., Corp., Co., etc.).
    """
    if "publisher" not in entry:
        return entry

    value = entry["publisher"].strip()
    if not value:
        return entry

    # Check if ends with period or period followed by closing brace
    if value.endswith("."):
        # Get the last word before the period
        # Handle both "word." and "word.}" cases
        text_before_period = value[:-1]
        last_word = _get_last_word(text_before_period)

        # If last word is 4 characters or less, it's likely an abbreviation - keep the period
        if len(last_word) <= 4:
            return entry

        # Remove trailing period for longer words
        entry["publisher"] = value[:-1]
    elif value.endswith(".}"):
        # Get the text before ".}"
        text_before_period = value[:-2]
        last_word = _get_last_word(text_before_period)

        # If last word is 4 characters or less, keep the period
        if len(last_word) <= 4:
            return entry

        # Remove period but keep closing brace
        entry["publisher"] = value[:-2] + "}"

    return entry


def _get_last_word(text: str) -> str:
    """Extract the last word from text, handling braces and punctuation.

    Examples:
    - "Academic Press" -> "Press"
    - "Company {LLC}" -> "LLC"
    - "Publisher Inc" -> "Inc"
    - "{ACM} Press" -> "Press"
    """
    if not text:
        return ""

    # Remove trailing/leading braces if they wrap the entire text
    text = text.strip()
    if text.startswith("{") and text.endswith("}") and _has_matching_outer_braces(text):
        text = text[1:-1]

    # Split on whitespace and get the last word
    words = text.split()
    if not words:
        return ""

    last_word = words[-1]

    # If the last word is wrapped in braces, extract the content
    if last_word.startswith("{") and last_word.endswith("}"):
        last_word = last_word[1:-1]

    # Remove non-alphabetic characters from the end for length calculation
    # but only count alphabetic characters for abbreviation detection
    return "".join(c for c in last_word if c.isalpha())


def fix_journal_periods(entry: BibEntry) -> BibEntry:
    """Remove trailing periods from journal field."""
    return remove_trailing_period(entry, "journal")


def fix_url_archiving(entry: BibEntry) -> BibEntry:
    """Archive URLs and add urldate field.

    For entries with 'url' field:
    1. If URL is not from web.archive.org, check for existing archive from today
    2. If no archive from today exists, create one using Wayback Machine
    3. Update URL to point to archived version
    4. Add/update urldate field with archive date in YYYY-MM-DD format
    """
    if "url" not in entry:
        return entry

    url = entry["url"].strip()
    if not url:
        return entry

    try:
        # Check if URL is already archived
        if is_wayback_url(url):
            # Extract date from wayback URL and set urldate
            archive_date = extract_wayback_date(url)
            if archive_date:
                entry["urldate"] = archive_date
            return entry

        # For non-archived URLs, get or create archive
        today = datetime.now().strftime("%Y%m%d")

        # Check if there's already an archive from today
        archived_url = get_wayback_snapshot(url, today)

        if not archived_url:
            # No archive from today, create one
            logger.info(f"Creating Wayback Machine archive for: {url}")
            archived_url = create_wayback_archive(url)

        if archived_url:
            entry["url"] = archived_url
            archive_date = extract_wayback_date(archived_url)
            if archive_date:
                entry["urldate"] = archive_date
        else:
            # Archive creation failed, add today's date anyway
            logger.warning(f"Failed to archive URL: {url}")
            entry["urldate"] = datetime.now().strftime("%Y-%m-%d")

    except Exception as e:
        logger.error(f"Error processing URL {url}: {e}")
        # If archiving fails, still add urldate for current date
        if "urldate" not in entry:
            entry["urldate"] = datetime.now().strftime("%Y-%m-%d")

    return entry


def is_wayback_url(url: str) -> bool:
    """Check if URL is a Wayback Machine URL."""
    return "web.archive.org" in url


def extract_wayback_date(wayback_url: str) -> str | None:
    """Extract date from Wayback Machine URL and format as YYYY-MM-DD.

    Example: https://web.archive.org/web/20231124182109/https://example.com
    Returns: 2023-11-24
    """
    try:
        # Pattern to match wayback URLs and extract timestamp (at least 8 digits for YYYYMMDD)
        pattern = r"web\.archive\.org/web/(\d{8,})"
        match = re.search(pattern, wayback_url)

        if match:
            timestamp = match.group(1)
            # Extract YYYYMMDD from timestamp (first 8 digits)
            date_str = timestamp[:8]
            # Validate that we have enough digits
            if len(date_str) == 8:
                # Convert to YYYY-MM-DD format
                year = date_str[:4]
                month = date_str[4:6]
                day = date_str[6:8]
                return f"{year}-{month}-{day}"

    except Exception as e:
        logger.error(f"Error extracting date from wayback URL {wayback_url}: {e}")

    return None


def get_wayback_snapshot(url: str, date_str: str) -> str | None:
    """Get Wayback Machine snapshot URL for given date (YYYYMMDD format).

    Uses the Wayback Machine API to check for existing snapshots.
    """
    try:
        # Use Wayback Machine availability API
        api_url = (
            f"https://archive.org/wayback/available?url={url}&timestamp={date_str}"
        )

        with httpx2.Client(timeout=30.0) as client:
            response = client.get(api_url)
            response.raise_for_status()

            data = response.json()
            if not isinstance(data, dict):
                return None

            archived_snapshots = data.get("archived_snapshots")
            if not isinstance(archived_snapshots, dict):
                return None

            snapshot = archived_snapshots.get("closest")
            if not isinstance(snapshot, dict):
                return None

            snapshot_url = snapshot.get("url")
            if snapshot.get("available") and isinstance(snapshot_url, str):
                # Check if the snapshot is from today
                snapshot_date = extract_wayback_date(snapshot_url)
                if snapshot_date == datetime.now().strftime("%Y-%m-%d"):
                    return snapshot_url

    except Exception as e:
        logger.error(f"Error checking wayback snapshot for {url}: {e}")

    return None


def create_wayback_archive(url: str) -> str | None:
    """Create a new Wayback Machine archive of the given URL.

    Uses the /save endpoint with screenshot enabled.
    """
    try:
        save_url = "https://web.archive.org/save"

        # Form data based on the HTML form analysis
        form_data = {
            "url": url,
            "capture_all": "0",  # Don't save error pages
            "capture_screenshot": "1",  # Save screenshot
        }

        with httpx2.Client(timeout=60.0) as client:
            response = client.post(save_url, data=form_data, follow_redirects=True)

            # The response might redirect to the archived page
            if response.status_code == 200 and "web.archive.org" in str(response.url):
                return str(response.url)

            # If we get a different response, try to extract the archive URL from headers
            if "Content-Location" in response.headers:
                content_location = response.headers["Content-Location"]
                if "web.archive.org" in content_location:
                    return str(content_location)

            # Last resort: construct expected archive URL
            today = datetime.now().strftime("%Y%m%d%H%M%S")
            return f"https://web.archive.org/web/{today}/{url}"

    except Exception as e:
        logger.error(f"Error creating wayback archive for {url}: {e}")

    return None
