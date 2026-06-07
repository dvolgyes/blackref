#!/usr/bin/env python3
"""Text formatting and wrapping utilities for BibTeX fields."""

import re
import textwrap

TEXT_FIELDS = (
    "abstract",
    "title",
    "booktitle",
    "journal",
    "publisher",
    "address",
    "notes",
    "note",
    "organization",
    "school",
    "institution",
)
NAME_FIELDS = ("author", "editor")
KEYWORD_FIELDS = ("keywords", "keyword")


def fix_paragraphs(text: str) -> str:
    """Fix paragraph formatting for structured abstracts."""
    text = re.sub(r"(\s(?P<pattern>BACKGROUND|Background))", r"\n\n\g<pattern>", text)
    text = re.sub(r"(\s(?P<pattern>METHODS|Methods))", r"\n\n\g<pattern>", text)
    text = re.sub(r"(\s(?P<pattern>CONCLUSION|Conclusion))", r"\n\n\g<pattern>", text)
    return re.sub(r"(\s(?P<pattern>RESULTS|Results))", r"\n\n\g<pattern>", text)


def fix_wrap(
    text: str, key: str, indent: int = 10, line_length: int = 100, relax: int = 10
) -> str:
    """Format and wrap text based on BibTeX field type."""
    original_text = text
    text = " ".join(text.split())  # removing all extra whitespaces

    # Only apply fix_paragraphs to abstract field
    if key.lower() == "abstract":
        text = fix_paragraphs(text)

    field_key = key.lower()
    wrapper = _make_wrapper(indent, line_length)

    if field_key in TEXT_FIELDS:
        return _format_text_field(
            text, original_text, indent, line_length, relax, wrapper
        )

    if field_key in NAME_FIELDS:
        return _format_names(text, indent)

    if field_key in KEYWORD_FIELDS:
        return _format_keywords(text, indent, relax, wrapper)

    return text.strip()


def _make_wrapper(indent: int, line_length: int) -> textwrap.TextWrapper:
    """Create the BibTeX field wrapper."""
    wrapper = textwrap.TextWrapper()
    wrapper.width = line_length - indent
    wrapper.break_long_words = False
    wrapper.break_on_hyphens = False
    return wrapper


def _format_text_field(
    text: str,
    original_text: str,
    indent: int,
    line_length: int,
    relax: int,
    wrapper: textwrap.TextWrapper,
) -> str:
    """Wrap long text fields while preserving reasonable manual line breaks."""
    original_lines = [
        line.strip() for line in original_text.split("\n") if line.strip()
    ]
    has_whitespace_only_lines = any(
        line.strip() == "" for line in original_text.split("\n")
    )

    preserved_text = _preserved_text(
        text, original_lines, has_whitespace_only_lines, indent, relax, wrapper
    )
    if preserved_text is not None:
        return preserved_text

    if len(text) <= wrapper.width + relax:
        return text.strip()

    parts = _wrapped_text_parts(text, has_whitespace_only_lines, line_length, wrapper)
    return _join_continuation_lines(parts, indent)


def _preserved_text(
    text: str,
    original_lines: list[str],
    has_whitespace_only_lines: bool,
    indent: int,
    relax: int,
    wrapper: textwrap.TextWrapper,
) -> str | None:
    """Return existing line breaks when they are already readable."""
    if len(original_lines) <= 1:
        return None

    average_line_length = len(text) / len(original_lines)
    is_too_broken_up = (
        len(original_lines) > 2 and average_line_length < wrapper.width // 3
    )
    if has_whitespace_only_lines or is_too_broken_up:
        return None

    line_lengths = [len(line.strip()) for line in original_lines]
    if (
        max(line_lengths) <= wrapper.width + relax
        and min(line_lengths) >= 10
        and max(line_lengths) - min(line_lengths) <= wrapper.width
    ):
        return _join_continuation_lines(original_lines, indent)

    return None


def _wrapped_text_parts(
    text: str,
    has_whitespace_only_lines: bool,
    line_length: int,
    wrapper: textwrap.TextWrapper,
) -> list[str]:
    """Wrap text with balanced two-line output when practical."""
    if has_whitespace_only_lines:
        return wrapper.wrap(text)

    text_length = len(text)
    if 2 * line_length <= text_length:
        return wrapper.wrap(text)

    best_break = _balanced_break_index(text)
    if best_break > 0:
        return [text[:best_break], text[best_break:]]

    return wrapper.wrap(text)


def _balanced_break_index(text: str) -> int:
    """Find a space near the midpoint that balances two wrapped lines."""
    mid_point = len(text) // 2
    search_range = min(30, len(text) // 3)
    best_break = -1
    min_length_diff = float("inf")

    for i in range(
        max(0, mid_point - search_range), min(len(text), mid_point + search_range)
    ):
        if text[i] != " ":
            continue

        first_line_len = i
        second_line_len = len(text) - i - 1
        length_diff = abs(first_line_len - second_line_len)

        if length_diff < min_length_diff:
            min_length_diff = length_diff
            best_break = i

    return best_break


def _format_names(text: str, indent: int) -> str:
    """Format author and editor names with aligned separators."""
    names = [name.strip() for name in text.strip().split(" and ")]
    if len(names) == 1:
        return names[0]

    longest_name_length = max(map(len, names))
    padded_names: list[str] = []
    for i, name in enumerate(names):
        if i == len(names) - 1:
            padded_names.append(name)
            continue

        k = longest_name_length - len(name)
        padded_names.append(name + (" " * k) + "  and")

    return _join_continuation_lines(padded_names, indent)


def _format_keywords(
    text: str, indent: int, relax: int, wrapper: textwrap.TextWrapper
) -> str:
    """Normalize keyword separators and wrap long keyword fields."""
    keyword_text = text.strip().replace(";", ",").replace(", ", ",")
    keyword_items = keyword_text.split(",")
    keywords = ", ".join(map(str.strip, keyword_items))

    if len(keywords) > wrapper.width + relax:
        result = _join_continuation_lines(wrapper.wrap(keywords), indent)
        return result.replace("_", " ")

    return keywords.replace("_", " ")


def _join_continuation_lines(parts: list[str], indent: int) -> str:
    """Join wrapped lines at the BibTeX continuation indentation."""
    continuation_indent = " " * (indent + 5)
    return f"\n{continuation_indent}".join(map(str.strip, parts))
