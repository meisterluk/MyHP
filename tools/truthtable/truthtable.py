#!/usr/bin/env python3

"""Visualize truthtable of a boolean function"""

import sys
import string
import inspect
import itertools
import collections

__ALL__ = ['Function', 'variation', 'evaluation', 'visualize', 'texify']


class Function:
    """Represents an anonymous function"""
    function = lambda a, b: a and b
    args = list(string.ascii_lowercase)

    def __init__(self, func, args=None, num_args=None):
        self.function = func
        if num_args is not None:
            self.args = list(string.ascii_lowercase)[0:num_args]
        if args is not None:
            self.args = args

    def __call__(self, *args, **kwargs):
        return self.function(*args, **kwargs)

    @property
    def num_args(self):
        return len(self.args)

    @num_args.setter
    def num_args(self, num_args):
        """Set arguments"""
        if num_args < len(self.args):
            self.args = self.args[0:num_args]
        else:
            assert num_args <= 26
            self.args = list(string.ascii_lowercase)[0:num_args]


def variation(variables=2, elements=(False, True)):
    """Create a possible configuration with `variables` `elements`"""
    for model in itertools.product(elements, repeat=variables):
        yield model


def evaluation(function):
    """Evaluate the value for each model and return ``model + value``"""
    for model in variation(function.num_args):
        yield list(model) + [function(*model)]


def visualize(f):
    """Visualize truthtable of a boolean function"""
    border = '+' + ('=' * 10 * f.num_args) + '+' + ('=' * 10) + '+'

    print('Function with {} variables created\n'.format(f.num_args))

    def field(text):
        print(' {} '.format(text).ljust(10), end='')

    def header(text):
        print(' {} '.format(text).center(10), end='')

    print(border)
    print('|', end='')
    for var in f.args:
        header(var)
    print('|', end='')
    header('func')
    print('|\n' + border)

    true = 0
    false = 0
    for row in evaluation(f):
        model = row[0:f.num_args]
        values = row[f.num_args:]
        assert len(values) == 1

        if values[0]:
            print("|\033[1;32m", end='')
        else:
            print("|\033[0;31m", end='')
        for v in model:
            field(str(v))
        print('|', end='')
        for v in values:
            if v:
                true += 1
            else:
                false += 1
            field(str(v))
        print("\033[0m|")
    print(border)

    print()
    print('{} models evaluate to True.'.format(true))
    print('{} models evaluate to False.\n'.format(false))


def texify(f):
    """Visualize truthtable of a boolean function"""

    def boolean(value):
        return value and r'\T' or r'\F'

    def line(elements):
        print('  ' + ' & '.join(elements) + r' \\ ')

    def field(text):
        return '{}'.format(text).ljust(10)

    print(r'\begin{table}')
    print(r' \begin{tabular}{' + ('c' * (f.num_args + 1)) + r'}')
    header = []
    for var in f.args:
        header.append(field(var))
    header.append(field('f_{}'.format(0)))
    line(header)
    print(r' \hline')

    for row in evaluation(f):
        line([field(boolean(r)) for r in row])

    print(r' \end{tabular}')
    print(r'\end{table}')


if __name__ == '__main__':
    if len(sys.argv) == 1:
        f = Function(lambda x, y: x and y, num_args=2)
        visualize(f)
    else:
        # read format and argv
        argv = sys.argv[1:]
        if argv[0].lower() == 'tex' or argv[0].lower() == 'latex':
            fmt = 'tex'
            argv = argv[1:]
        elif sys.argv[0] == 'plain':
            fmt = 'plain'
            argv = argv[1:]
        else:
            fmt = 'plain'

        # create 1 function
        argv = ' '.join(argv)
        variables = argv.split(':')[0].split(',')
        variables = [v.strip() for v in variables]

        func = eval('lambda ' + argv)

        function = Function(func, args=variables)

        # create visualization
        if fmt == 'tex':
            texify(function)
        else:
            visualize(function)
