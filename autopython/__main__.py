#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import argparse
import os.path
import sys

from autopython import Presenter, VERSION
from autopython.cpython import PresenterShell

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--version', action='version',
                        version='AutoPython ' + VERSION)
    parser.add_argument('-c', '--color-scheme', default='default',
                        help='Highligh code using the specified color scheme.')
    parser.add_argument('-i', '--ipython', dest='ipython', default=False,
                        action='store_true',
                        help='Use IPython for the interactive shell.')
    parser.add_argument('-d', '--delay', type=int, default=30,
                        help='Delay (in ms) between every simulated '
                             'keystroke.')
    parser.add_argument('-l', '--lines', type=int, default=1,
                        help='How many lines are kept after pagination.')
    parser.add_argument('--no-log', dest='logging', default=True,
                        action='store_false', help='Disable logging every '
                        'action during the presentation.')
    parser.add_argument('--no-highlight', dest='highlight', default=True,
                        action='store_false',
                        help='Disable code highlighting.')
    parser.add_argument('--no-pagination', dest='pagination', default=True,
                        action='store_false',
                        help='Disable code pagination.')
    parser.add_argument('SOURCE')
    args = parser.parse_args()

    if not os.path.exists(args.SOURCE):
        _, ext = os.path.splitext(args.SOURCE)
        if not ext and not os.path.exists(args.SOURCE + '.py'):
            print("{}: file not found: '{}'".format(parser.prog, args.SOURCE),
                  file=sys.stderr)
            sys.exit(1)
        args.SOURCE += '.py'

    color_scheme = args.color_scheme if args.highlight else None
    shell = PresenterShell(color_scheme=color_scheme, use_ipython=args.ipython)

    presenter = Presenter(shell, logging=args.logging, context_lines=args.lines,
                          paginate=args.pagination, typing_delay=args.delay)
    try:
        presenter.load_file(args.SOURCE)
    except OSError as exc:
        print("{}: can't open file '{}'".format(parser.prog, args.SOURCE), exc,
              sep='\n', file=sys.stderr)
        sys.exit(1)
    except SyntaxError as exc:
        print('  File "{}"\nSyntaxError: {}'.format(args.SOURCE, exc),
              file=sys.stderr)
        sys.exit(1)
    presenter.run()


if __name__ == '__main__':
    main()
