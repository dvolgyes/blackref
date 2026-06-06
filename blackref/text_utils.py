#!/usr/bin/env python3
"""Text formatting and wrapping utilities for BibTeX fields."""

import re
import textwrap


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
    # First normalize whitespace and check for issues
    original_text = text
    text = " ".join(text.split())  # removing all extra whitespaces

    # Check if we had whitespace-only lines in original text
    has_whitespace_only_lines = any(
        line.strip() == "" for line in original_text.split("\n")
    )

    # Only apply fix_paragraphs to abstract field
    if key.lower() == "abstract":
        text = fix_paragraphs(text)

    wrapper = textwrap.TextWrapper()
    wrapper.width = line_length - indent
    wrapper.break_long_words = False
    wrapper.break_on_hyphens = False

    # Fields that commonly contain long text that might be wrapped across multiple lines
    text_fields = [
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
    ]

    # For text fields, check if we should preserve existing formatting first
    if key.lower() in text_fields:
        # Check if text is too broken up (too many lines for the content length)
        original_lines = [
            line.strip() for line in original_text.split("\n") if line.strip()
        ]

        # If we have multiple lines, check if we should preserve the existing formatting
        if len(original_lines) > 1:
            # Only consider "too broken up" if we have more than 2 lines AND average line length is very short
            average_line_length = (
                len(text) / len(original_lines) if original_lines else 0
            )
            min_reasonable_line_length = (
                wrapper.width // 3
            )  # Very conservative threshold
            is_too_broken_up = (
                len(original_lines) > 2
                and average_line_length < min_reasonable_line_length
            )

            # Check if existing formatting is already acceptable
            if not has_whitespace_only_lines and not is_too_broken_up:
                # Check if existing lines are within acceptable length ranges
                max_line_len = max(len(line.strip()) for line in original_lines)
                min_line_len = min(len(line.strip()) for line in original_lines)
                line_length_diff = max_line_len - min_line_len

                # If existing formatting is reasonable, preserve it
                # Be quite lenient about preserving existing formatting
                if (
                    max_line_len <= wrapper.width + relax
                    and min_line_len
                    >= 10  # Very minimal threshold - just avoid single words
                    and line_length_diff <= wrapper.width  # Very lenient for balance
                ):
                    # Preserve existing line breaks but clean up whitespace
                    continuation_indent = " " * (indent + 5)
                    return f"\n{continuation_indent}".join(
                        line.strip() for line in original_lines
                    )

    # Apply normal wrapping logic only if text is long enough
    if key.lower() in text_fields and len(text) > wrapper.width + relax:
        # Only use balanced approach if we don't have whitespace-only lines and text isn't too broken up
        if not has_whitespace_only_lines:
            # Use balanced line length approach
            text_length = len(text)
            if 2 * line_length > text_length:
                # Find optimal break point that minimizes line length difference
                mid_point = text_length // 2
                search_range = min(30, text_length // 3)  # Wider search range
                best_break = -1
                min_length_diff = float("inf")

                # Search around midpoint for optimal balance
                for i in range(
                    max(0, mid_point - search_range),
                    min(len(text), mid_point + search_range),
                ):
                    if i < len(text) and text[i] == " ":
                        first_line_len = i
                        second_line_len = text_length - i - 1  # -1 for the space
                        length_diff = abs(first_line_len - second_line_len)

                        if length_diff < min_length_diff:
                            min_length_diff = length_diff
                            best_break = i

                if best_break > 0:
                    parts = [text[:best_break], text[best_break:]]
                else:
                    parts = wrapper.wrap(text)
            else:
                parts = wrapper.wrap(text)
        else:
            # Use standard textwrap for proper word boundary handling
            parts = wrapper.wrap(text)

        # Align continuation lines with opening brace position
        continuation_indent = " " * (indent + 5)
        return f"\n{continuation_indent}".join(map(str.strip, parts))

    if key.lower() in ["author", "editor"]:
        names = text.strip().split(" and ")
        names = [name.strip() for name in names]
        if len(names) == 1:
            return names[0]

        author_indent = " " * (indent + 5)

        longest_name_length = max(map(len, names))
        padded_names: list[str] = []
        for i, name in enumerate(names):
            if i == len(names) - 1:  # Last name, no "and"
                padded_names.append(name)
            else:  # Add padding and "and"
                k = longest_name_length - len(name)
                padded_names.append(name + (" " * k) + "  and")
        return f"\n{author_indent}".join(padded_names)

    if key.lower() in ["keywords", "keyword"]:
        keyword_text = text.strip().replace(";", ",").replace(", ", ",")
        keyword_items = keyword_text.split(",")
        keywords = ", ".join(map(str.strip, keyword_items))

        if len(keywords) > wrapper.width + relax:
            parts = wrapper.wrap(keywords)
            # Align continuation lines with opening brace position
            continuation_indent = " " * (indent + 5)
            result = f"\n{continuation_indent}".join(map(str.strip, parts))
            return result.replace("_", " ")

        return keywords.replace("_", " ")

    return text.strip()
