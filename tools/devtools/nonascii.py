#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import io
import os
import re
import sys
import argparse
import unicodedata

TEMPLATE = '''{char} on line {lineno}
  Category:       {cat}
  Unicode point:  {point}
  Name:           {name}
  In cp1252:      {cp1252}
  In UTF-8:       {utf8}
  In UTF-16:      {utf16}
  In UTF-32:      {utf32}
  NFC normalized: {normalized}
'''



def print_nonascii_bytes(content):
    pass

def print_nonascii_text(content):
    def cp1252(c):
        try:
            byte = c.encode('cp1252')
            return '{} (dec={})'.format(str(byte), ord(byte))
        except UnicodeEncodeError:
            return 'not encodable'

    def out(c, lineno):
        try:
            rep = TEMPLATE.format(**{
                'char': c,
                'lineno': lineno,
                'cat': unicodedata.category(c),
                'point': 'U+{} [dec={}]'.format(hex(ord(c)).upper()[2:], ord(c)),
                'name': unicodedata.name(c),
                'cp1252': cp1252(c),
                'utf8': c.encode('utf-8'),
                'utf16': c.encode('utf-16'),
                'utf32': c.encode('utf-32'),
                'normalized': unicodedata.normalize('NFC', c)
            })
            print(rep)
        except (UnicodeEncodeError, ValueError):
            err = 'On line {} is some character I cannot even analyze: {}'
            print(err.format(lineno, c), file=sys.stderr, end=os.linesep * 2)

    for lineno, line in enumerate(content.splitlines(keepends=True)):
        for char in line:
            if not (0 <= ord(char) <= 127):
                out(char, lineno)


def main(args):
    if args.binary:
        with open(args.file, 'rb') as fp:
            print_nonascii_bytes(fp.read())
    else:
        with io.open(args.file, encoding=args.encoding) as fp:
            print_nonascii_text(fp.read())

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help="the file to analyze")
    parser.add_argument('-e', '--encoding', type=str, default="utf-8", help="The character set of file")
    parser.add_argument('-b', '--binary', type=str, help="Read file as binary file (no encoding needed)")
    sys.exit(main(parser.parse_args()))
