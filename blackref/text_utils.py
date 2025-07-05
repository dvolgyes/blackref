#!/usr/bin/env python3
"""Text formatting and wrapping utilities for BibTeX fields."""

import re
import textwrap


def fix_paragraphs(text: str) -> str:
    """Fix paragraph formatting for structured abstracts."""
    text = re.sub(r"(\s(?P<pattern>BACKGROUND|Background))", r"\n\n\g<pattern>", text)
    text = re.sub(r"(\s(?P<pattern>METHODS|Methods))", r"\n\n\g<pattern>", text)
    text = re.sub(r"(\s(?P<pattern>CONCLUSION|Conclusion))", r"\n\n\g<pattern>", text)
    text = re.sub(r"(\s(?P<pattern>RESULTS|Results))", r"\n\n\g<pattern>", text)
    return text


def fix_wrap(
    text: str, key: str, indent: int = 10, line_length: int = 80, relax: int = 10
) -> str:
    """Format and wrap text based on BibTeX field type."""
    text = " ".join(text.split())  # removing all extra whitespaces
    text = fix_paragraphs(text)
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
            p = text[N // 2 :].find(" ")
            if p >= 0:
                p += N // 2
                parts = [text[:p], text[p:]]
            else:
                parts = wrapper.wrap(text)
        else:
            parts = wrapper.wrap(text)

        # Align continuation lines with opening brace position
        continuation_indent = " " * (indent + 5)
        result = f"\n{continuation_indent}".join(map(str.strip, parts))
        return result

    if key.lower() in ["author", "editor"]:
        names = text.strip().split(" and ")
        names = [name.strip() for name in names]
        if len(names) == 1:
            return names[0]

        author_indent = " " * (indent + 5)

        N = max(map(len, names))
        padded_names = []
        for i, name in enumerate(names):
            if i == len(names) - 1:  # Last name, no "and"
                padded_names.append(name)
            else:  # Add padding and "and"
                k = N - len(name)
                padded_names.append(name + (" " * k) + "  and")
        result = f"\n{author_indent}".join(padded_names)
        return result

    if key.lower() in ["keywords", "keyword"]:
        keywords = text.strip().replace(";", ",").replace(", ", ",")
        keywords = keywords.split(",")
        keywords = ", ".join(map(str.strip, keywords))
        parts = wrapper.wrap(keywords)
        # Align continuation lines with opening brace position
        continuation_indent = " " * (indent + 5)
        result = f"\n{continuation_indent}".join(map(str.strip, parts))
        return result.replace("_", " ")

    return text.strip()
