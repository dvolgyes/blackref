#!/usr/bin/env python3
"""Command-line interface for blackref."""

import sys
from pathlib import Path
import click
import bibtexparser
from .formatter import formatter


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
    if (
        src != sys.stdin
        and hasattr(src, "name")
        and src.name
        and src.name != "<stdin>"
        and not Path(src.name).exists()
    ):
        click.echo(f"Invalid input file: {src.name}", err=True)
        sys.exit(-1)

    # Process the BibTeX file
    content = src.read()
    bib = bibtexparser.loads(content)
    formatted_output = formatter(
        bib, display_order_fields, sort_fields, utf8_fields, latex_fields
    )

    output.write(formatted_output)

    # Close output if we opened it for write-back
    if write_back and output != sys.stdout:
        output.close()
