#!/usr/bin/env python3

try:
    import sys
    from pathlib import Path
    import textwrap
    import re
    import configargparse
    import bibtexparser
    import isbnlib
    from pylatexenc.latex2text import LatexNodes2Text
    from pylatexenc.latexencode import unicode_to_latex
except ImportError:
    sys.stderr.write('Some libraries are missing.\n')


__version__ = '0.1.7'
__author__ = 'David Völgyes'
__email__ = 'david.volgyes@ieee.org'
__license__ = 'AGPLv3'
__summary__ = 'An uncompromising BibTeX/BibLaTeX reference list formatter.'
__description__ = __summary__


def eprint(*args, **kwargs):
    print(*args, **kwargs, file=sys.stderr)# noqa:  T001


def fix_paragraphs(text):
    text = re.sub(r'(\s(?P<pattern>BACKGROUND|Background))', r'\n\n\g<pattern>', text)
    text = re.sub(r'(\s(?P<pattern>METHODS|Methods))', r'\n\n\g<pattern>', text)
    text = re.sub(r'(\s(?P<pattern>CONCLUSION|Conclusion))', r'\n\n\g<pattern>', text)
    text = re.sub(r'(\s(?P<pattern>RESULTS|Results))', r'\n\n\g<pattern>', text)
    return text


def fix_wrap(text, key, indent=10, line_length=80, relax=10):
    text = ' '.join(text.split())  # removing all extra whitespaces
    text = fix_paragraphs(text)
    wrapper = textwrap.TextWrapper()
    wrapper.width = line_length - indent
    wrapper.break_long_words = False
    wrapper.break_on_hyphen = False
    indent_text = ' ' * indent

    if (key.lower() in ['abstract', 'title', 'booktitle']
            and len(text) > wrapper.width + relax):
        N = len(text)
        if N < 2 * line_length:
            p = text[N // 2:].find(' ')
            if p >= 0:
                p += N // 2
                parts = [text[:p], text[p:]]
            else:
                parts = wrapper.wrap(text)
        else:
            parts = wrapper.wrap(text)
        result = f'\n{indent_text}'.join(map(str.strip, parts))
        return result

    if key.lower() in ['author', 'editor']:
        names = text.strip().split(' and ')
        N = max(map(len, map(str.strip, names)))
        padded_names = []
        for name in names:
            k = N - len(name)
            padded_names.append(name + (' ' * k))
        result = f'  and\n{indent_text}'.join(padded_names).strip()
        return result

    if key.lower() in ['keywords', 'keyword']:
        keywords = text.strip().replace(';', ',').replace(', ', ',')
        keywords = keywords.split(',')
        keywords = ', '.join(map(str.strip, keywords))
        parts = wrapper.wrap(keywords)
        result = f'\n{indent_text}'.join(map(str.strip, parts))
        return result.replace('_', ' ')

    return text.strip()


def fix_isbn(entry):
    if 'isbn' in entry:
        value = entry['isbn']
        if isbnlib.is_isbn10(value):
            value = isbnlib.to_isbn13(value)
        if not isbnlib.is_isbn13(value):
            raise Exception(f'invalid isbn in {entry["ID"]}: {entry["isbn"]}')
        entry['isbn'] = isbnlib.mask(value, separator='-')
    return entry


def fix_issn(entry):
    if 'issn' in entry:
        value = entry['issn'].replace('-', '')
        value = value[0:4] + '-' + value[4:]
        if len(value) != 9:
            raise Exception(f'invalid issn in {entry["ID"]}: {entry["issn"]}')
        entry['issn'] = value
    return entry


def fix_pages(entry):
    if 'pages' in entry:
        value = entry['pages'].replace(' ', '')
        re.sub(r'([^-])-([^-])', r'r\g<1>--\g<2>', value)
        entry['pages'] = value
    return entry


def remove_empty_keys(entry):
    for key in list(entry.keys()):
        if entry[key] is None:
            entry[key] = ''
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
    return fix_utf8_field(entry, 'author', args)


def fix_abstract(entry, args):
    return fix_utf8_field(entry, 'abstract', args)


def formatter(bib, args):
    display_order, sort = args.display_order, args.sort
    writer = bibtexparser.bwriter.BibTexWriter()
    writer.add_trailing_comma = True
    writer.display_order = display_order
    writer.order_entries_by = None
    writer.align_values = 10
    writer.indent = ' '
    writer.contents = ['preambles', 'entries', 'strings']

    max_key_length = 0
    for entry in bib.entries:
        entry = remove_empty_keys(entry)
        entry = fix_authors(entry, args)
        entry = fix_abstract(entry, args)
        entry = fix_isbn(entry)
        entry = fix_issn(entry)
        entry = fix_pages(entry)
        for key in entry.keys():
            max_key_length = max(max_key_length, len(key) + len(writer.indent) + 4)

    for entry in bib.entries:
        for key in entry.keys():
            entry[key] = fix_wrap(entry[key], key, indent=max_key_length)

    for skey in reversed(sort):
        reverse = skey[-1] == '-'
        if reverse:
            skey = skey[:-1]
        bib.entries = sorted(bib.entries,
                             key=lambda x: x.get(skey, '').lower(),
                             reverse=reverse)

    return writer.write(bib)


def main(cli_args=None):
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

    parser = configargparse.ArgParser(
        auto_env_var_prefix='BLACKREF_',
        add_env_var_help=True,
        add_config_file_help=True,
        default_config_files=['~/.config/blackref.conf'],
        description='The uncompromising reference formatter.'
    )

    parser.add_argument(
        '-c', '--config',
        is_config_file=True,
        dest='configfile',
        help='Config file with "key: value" items.'
             ' CLI options have higher precedence than config values.')

    parser.add_argument(
        '-w', '--write-back',
        dest='writeback',
        action='store_true',
        help='Write modifications back to the original file.',
        default=False
    )

    parser.add_argument(
        '-U', '--utf8',
        dest='utf8',
        metavar='FIELD[,FIELD]',
        help='Comma separated fieldnames for UTF8 encoding. Default: abstract',
        default='abstract'
    )

    parser.add_argument(
        '-L', '--latex',
        dest='latex',
        metavar='FIELD[,FIELD]',
        help='Comma separated fieldnames for LaTeX encoding. Default: author,title',
        default='author,title'
    )

    parser.add_argument(
        '-o',
        '--output',
        dest='output',
        metavar='DST',
        type=str,
        help='output file',
        default=sys.stdout,
    )

    parser.add_argument(
        '-s',
        '--sort',
        dest='sort',
        metavar='KEYS',
        type=str,
        help='Comma separated list of BibTeX fields for sorting entries.'
             ' Default: ID',
        default='ID'
    )

    order = ','.join(('title',
                      'booktitle',
                      'author',
                      'editor',
                      'abstract',
                      'journal',
                      'issn',
                      'volume',
                      'year',
                      'month',
                      'number',
                      'pages',
                      'publisher',
                      'address',
                      'doi',
                      'pubmedid',
                      'url',
                      'notes'))

    parser.add_argument(
        '-d',
        '--display-order',
        dest='display_order',
        metavar='FIELDS',
        type=str,
        help=f'Order of display for BibTeX fields. Default: {order}',
        default=order
    )

    parser.add_argument(
        'src',
        metavar='SRC',
        nargs='?',
        type=str,
        help='source file',
        default=sys.stdin
    )

    if cli_args is not None:
        args = parser.parse_args(cli_args)
    else:
        args = parser.parse_args()

    args.sort = tuple(x.strip() for x in args.sort.split(','))
    args.utf8 = {x.strip() for x in args.utf8.lower().split(',')}
    args.latex = {x.strip() for x in args.latex.lower().split(',')}
    args.utf8 = args.utf8 - args.latex
    args.display_order = tuple(x.strip() for x in args.display_order.split(','))

    if args.writeback:
        if args.output == sys.stdout and args.src != sys.stdin:
            args.output = args.src

    if args.src != sys.stdin and not Path(args.src).exists():
        eprint(f'Invalid input file: {args.src}')
        sys.exit(-1)

    with LazyOpen(args.src, 'rt') as fh:
        bib = bibtexparser.loads(fh.read())

    with LazyOpen(args.output, 'wt') as f:
        f.write(formatter(bib, args))
