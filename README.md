# Blackref: An Uncompromising BibTeX/BibLaTeX Formatter

<p>
  <a href="https://github.com/dvolgyes/blackref/actions/workflows/test.yml"><img alt="CI" src="https://github.com/dvolgyes/blackref/actions/workflows/test.yml/badge.svg" /></a>
  <a href="https://coveralls.io/github/dvolgyes/blackref?branch=main"><img alt="Coverage Status" src="https://coveralls.io/repos/github/dvolgyes/blackref/badge.svg?branch=main" /></a>
  &nbsp;&nbsp;&nbsp;&nbsp;
  <a href="https://pypi.org/project/blackref/"><img alt="Version: 0.2.0" src="https://img.shields.io/badge/version-0.2.0-orange.svg" /></a>
  <a href="https://pypi.org/project/blackref/"><img alt="Status: Beta" src="https://img.shields.io/badge/status-beta-yellow.svg" /></a>
  &nbsp;&nbsp;&nbsp;&nbsp;
  <a href="LICENSE.txt"><img alt="License: AGPL-3.0" src="https://img.shields.io/badge/license-AGPL--3.0-green.svg" /></a>
  <a href="https://www.python.org/"><img alt="Python: >=3.12,<3.15" src="https://img.shields.io/badge/python-%3E=3.12%2C%3C3.15-blue.svg" /></a>
</p>

`blackref` is a command-line tool that automatically formats your BibTeX and BibLaTeX files to be consistent, readable, and clean. Inspired by the `black` code formatter for Python, it enforces a strict, opinionated style, leaving no room for configuration. This ensures that your reference files are always perfectly formatted, allowing you to focus on the content, not the style.

## Key Features

- **Consistent Formatting**: Automatically formats your entire BibTeX/BibLaTeX file.
- **Entry Sorting**: Sorts the entries in your bibliography (e.g., by entry ID).
- **Field Ordering**: Arranges the fields within each entry in a consistent, logical order.
- **Smart Encoding**: Handles both UTF-8 and LaTeX encoding for specified fields.
- **In-place Modification**: Can modify files directly for convenience.
- **Unix Philosophy**: Reads from `stdin` and writes to `stdout` by default, making it easy to pipe and integrate into scripts.

## Usage

Run the package directly with `uvx`:

```bash
uvx blackref my_references.bib
```

You can also use it with pipes:

```bash
cat my_references.bib | uvx blackref > formatted_references.bib
```

To modify a file directly, use write-back mode:

```bash
uvx blackref --write-back my_references.bib
```

You can specify which fields to sort the entries by. The default is to sort by
the BibTeX entry ID (`ID`).

```bash
uvx blackref --sort "author,year" my_references.bib
```

`blackref` uses a default order for fields within each entry. You can override
this with the `--display-order` option.

```bash
uvx blackref --display-order "author,title,year,journal" my_references.bib
```

## Pre-commit hooks

You can format BibTeX and BibLaTeX files automatically before committing them to
git.

```yaml
repos:
- repo: https://github.com/dvolgyes/blackref
  rev: v0.2.0
  hooks:
  - id: blackref
```

## Complementary Tool: `reflint`

For linting and checking the semantic content of your reference files (e.g., missing fields, incorrect values), check out the complementary tool, [reflint](https://github.com/dvolgyes/reflint). `reflint` fixes the content, while `blackref` fixes the style.

## License

`blackref` is licensed under the AGPL-3.0 License. See the [LICENSE.txt](LICENSE.txt) file for details.
