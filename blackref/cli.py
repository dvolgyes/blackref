#!/usr/bin/env python3
"""Command-line interface for blackref."""

from pathlib import Path
from typing import TextIO

import click
import bibtexparser

from .formatter import formatter


DEFAULT_ORDER = (
    "title,booktitle,author,editor,abstract,journal,issn,volume,year,month,"
    "number,pages,publisher,address,doi,pubmedid,url,notes"
)


def _format_content(
    content: str,
    *,
    display_order_fields: tuple[str, ...],
    sort_fields: tuple[str, ...],
    utf8_fields: set[str],
    latex_fields: set[str],
    formatting_mode: str,
    wayback: bool,
) -> str:
    """Format one BibTeX document."""
    bib = bibtexparser.loads(content)
    return formatter(
        bib,
        display_order_fields,
        sort_fields,
        utf8_fields,
        latex_fields,
        formatting_mode,
        wayback,
    )


@click.command()
@click.argument(
    "src",
    nargs=-1,
    type=click.Path(exists=True, dir_okay=False),
)
@click.option(
    "-w",
    "--write-back",
    is_flag=True,
    help="Write modifications back to the original file.",
)
@click.option(
    "--basic",
    "formatting_mode",
    flag_value="basic",
    help="Apply only indentation and sorting (field and entry).",
)
@click.option(
    "--full",
    "formatting_mode",
    flag_value="full",
    default=True,
    help="Apply all formatting rules and changes (default).",
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
@click.option("-o", "--output", type=click.File("w"), default="-", help="Output file.")
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
@click.option(
    "--wayback",
    is_flag=True,
    help="Archive URLs using Wayback Machine and add urldate fields.",
)
def main(
    src: tuple[str, ...],
    write_back: bool,
    formatting_mode: str,
    utf8: str,
    latex: str,
    output: TextIO,
    sort: str,
    display_order: str,
    wayback: bool,
) -> None:
    """The uncompromising reference formatter."""
    sort_fields = tuple(x.strip() for x in sort.split(","))
    utf8_fields = {x.strip() for x in utf8.lower().split(",")}
    latex_fields = {x.strip() for x in latex.lower().split(",")}
    latex_fields = latex_fields - utf8_fields
    display_order_fields = tuple(x.strip() for x in display_order.split(","))

    if not src and write_back:
        raise click.ClickException("--write-back requires at least one input file.")

    if len(src) > 1 and not write_back:
        raise click.ClickException("Multiple input files require --write-back.")

    if not src:
        content = click.get_text_stream("stdin").read()
        formatted_output = _format_content(
            content,
            display_order_fields=display_order_fields,
            sort_fields=sort_fields,
            utf8_fields=utf8_fields,
            latex_fields=latex_fields,
            formatting_mode=formatting_mode,
            wayback=wayback,
        )
        output.write(formatted_output)
        return

    if write_back:
        for path in (Path(item) for item in src):
            formatted_output = _format_content(
                path.read_text(encoding="utf-8"),
                display_order_fields=display_order_fields,
                sort_fields=sort_fields,
                utf8_fields=utf8_fields,
                latex_fields=latex_fields,
                formatting_mode=formatting_mode,
                wayback=wayback,
            )
            path.write_text(formatted_output, encoding="utf-8")
        return

    formatted_output = _format_content(
        Path(src[0]).read_text(encoding="utf-8"),
        display_order_fields=display_order_fields,
        sort_fields=sort_fields,
        utf8_fields=utf8_fields,
        latex_fields=latex_fields,
        formatting_mode=formatting_mode,
        wayback=wayback,
    )
    output.write(formatted_output)
