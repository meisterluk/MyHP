#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'meisterluk <admin@lukas-prokop.at>'
__version__ = '0.0.1-alpha'

import io
import sys
import argparse

def sort_lines(content, *, start="", end=""):
    sort_now = not start
    cache = []

    def dump_cache():
        nonlocal sort_now, cache
        if cache:
            cache.sort(key=lambda x: x.strip())
            yield from cache
            cache = []
        sort_now = False

    for line in content.splitlines():
        if sort_now:
            if end and end in line:
                yield from dump_cache()
                yield line
            else:
                cache.append(line)
        else:
            if start in line:
                sort_now = True
            yield line
    
    yield from dump_cache()

def main(args):
    with io.open(args.file, encoding=args.encoding) as fp:
        content = fp.read()
        for line in sort_lines(content, start=args.start, end=args.end):
            print(line)
    return 0

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help="the file to sort content from")
    parser.add_argument('-e', '--encoding', type=str, default="utf-8", help="The character set of file")
    parser.add_argument('-s', '--start', type=str, help="Sorting starts after the first line containing this string")
    parser.add_argument('-f', '--end', type=str, help="Sorting ends before the first line containing this string")
    sys.exit(main(parser.parse_args()))
