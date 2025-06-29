#!/usr/bin/env python3

try:
    import sys
    from pathlib import Path
    import textwrap
    import re
    import click
    import bibtexparser
    import isbnlib
    from pylatexenc.latex2text import LatexNodes2Text
    from pylatexenc.latexencode import unicode_to_latex
except ImportError:
    sys.stderr.write("Some libraries are missing.\n")


try:
    from importlib.metadata import version

    __version__ = version("blackref")
except ImportError:
    # Fallback for older Python versions or when package is not installed
    __version__ = "unknown"
__author__ = "David Völgyes"
__email__ = "david.volgyes@ieee.org"
__license__ = "AGPLv3"
__summary__ = "An uncompromising BibTeX/BibLaTeX reference list formatter."
__description__ = __summary__


def eprint(*args, **kwargs):
    print(*args, **kwargs, file=sys.stderr)  # noqa:  T001


def fix_paragraphs(text):
    text = re.sub(r"(\s(?P<pattern>BACKGROUND|Background))", r"\n\n\g<pattern>", text)
    text = re.sub(r"(\s(?P<pattern>METHODS|Methods))", r"\n\n\g<pattern>", text)
    text = re.sub(r"(\s(?P<pattern>CONCLUSION|Conclusion))", r"\n\n\g<pattern>", text)
    text = re.sub(r"(\s(?P<pattern>RESULTS|Results))", r"\n\n\g<pattern>", text)
    return text


def fix_wrap(text, key, indent=10, line_length=80, relax=10):
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
        result = f"\n{indent_text}".join(map(str.strip, parts))
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
        result = f"\n{indent_text}".join(map(str.strip, parts))
        return result.replace("_", " ")

    return text.strip()


def fix_isbn(entry):
    if "isbn" in entry:
        value = entry["isbn"]
        if isbnlib.is_isbn10(value):
            value = isbnlib.to_isbn13(value)
        if not isbnlib.is_isbn13(value):
            raise Exception(f"invalid isbn in {entry['ID']}: {entry['isbn']}")
        entry["isbn"] = isbnlib.mask(value, separator="-")
    return entry


def fix_issn(entry):
    if "issn" in entry:
        value = entry["issn"].replace("-", "")
        value = value[0:4] + "-" + value[4:]
        if len(value) != 9:
            raise Exception(f"invalid issn in {entry['ID']}: {entry['issn']}")
        entry["issn"] = value
    return entry


def fix_pages(entry):
    if "pages" in entry:
        value = entry["pages"].replace(" ", "")
        re.sub(r"([^-])-([^-])", r"r\g<1>--\g<2>", value)
        entry["pages"] = value
    return entry


def remove_empty_keys(entry):
    for key in list(entry.keys()):
        if entry[key] is None:
            entry[key] = ""
        v = str(entry[key]).strip()
        if len(v) == 0:
            entry.pop(key)
    return entry


def fix_utf8_field(entry, field, args):
    if field not in entry:
        return entry

    value = entry[field]
    if field is args.utf8:
        value = LatexNodes2Text().latex_to_text(value)
    elif field is args.latex:
        value = unicode_to_latex(value)
    entry[field] = value

    return entry


def fix_authors(entry, args):
    return fix_utf8_field(entry, "author", args)


def fix_abstract(entry, args):
    return fix_utf8_field(entry, "abstract", args)


def formatter(bib, args):
    display_order, sort = args.display_order, args.sort
    writer = bibtexparser.bwriter.BibTexWriter()
    writer.add_trailing_comma = True
    writer.display_order = display_order
    writer.order_entries_by = None
    writer.indent = " "
    writer.contents = ["preambles", "entries", "strings"]

    max_key_length = 10  # Minimum alignment
    for entry in bib.entries:
        entry = remove_empty_keys(entry)
        entry = fix_authors(entry, args)
        entry = fix_abstract(entry, args)
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

    for skey in reversed(sort):
        reverse = skey[-1] == "-"
        if reverse:
            skey = skey[:-1]
        bib.entries = sorted(
            bib.entries, key=lambda x: x.get(skey, "").lower(), reverse=reverse
        )

    return writer.write(bib)


class LazyOpen:
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


DEFAULT_ORDER = ",".join(
    [
        "title",
        "booktitle",
        "author",
        "editor",
        "abstract",
        "journal",
        "issn",
        "volume",
        "year",
        "month",
        "number",
        "pages",
        "publisher",
        "address",
        "doi",
        "pubmedid",
        "url",
        "notes",
    ]
)


@click.command()
@click.argument("src", type=click.File("r"), default=sys.stdin)
@click.option(
    "-w",
    "--write-back",
    is_flag=True,
    help="Write modifications back to the original file.",
)
@click.option(
    "-U",
    "--utf8",
    default="abstract",
    help="Comma separated fieldnames for UTF8 encoding.",
)
@click.option(
    "-L",
    "--latex",
    default="author,title",
    help="Comma separated fieldnames for LaTeX encoding.",
)
@click.option(
    "-o", "--output", type=click.File("w"), default=sys.stdout, help="Output file."
)
@click.option(
    "-s",
    "--sort",
    default="ID",
    help="Comma separated list of BibTeX fields for sorting entries.",
)
@click.option(
    "-d",
    "--display-order",
    default=DEFAULT_ORDER,
    help="Order of display for BibTeX fields.",
)
def main(src, write_back, utf8, latex, output, sort, display_order):
    """The uncompromising reference formatter."""

    # Process arguments
    sort_fields = tuple(x.strip() for x in sort.split(","))
    utf8_fields = {x.strip() for x in utf8.lower().split(",")}
    latex_fields = {x.strip() for x in latex.lower().split(",")}
    utf8_fields = utf8_fields - latex_fields
    display_order_fields = tuple(x.strip() for x in display_order.split(","))

    # Handle write-back logic
    if write_back and output == sys.stdout and src != sys.stdin:
        output = open(src.name, "w")

    # Validate input file
    if src != sys.stdin and not Path(src.name).exists():
        click.echo(f"Invalid input file: {src.name}", err=True)
        sys.exit(-1)

    # Create args object compatible with existing formatter
    class Args:
        def __init__(self):
            self.sort = sort_fields
            self.utf8 = utf8_fields
            self.latex = latex_fields
            self.display_order = display_order_fields

    args = Args()

    # Process the BibTeX file
    bib = bibtexparser.loads(src.read())
    formatted_output = formatter(bib, args)

    output.write(formatted_output)

    # Close output if we opened it for write-back
    if write_back and output != sys.stdout:
        output.close()
