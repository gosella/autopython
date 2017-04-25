# -*- coding: utf-8 -*-

from __future__ import print_function

import sys

try:
    import queue
except ImportError:
    import Queue as queue


PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

if sys.version_info[:2] < (3, 3):
    _real_print = print

    def print(*objects, **kwargs):
        sep = kwargs.get('sep', ' ')
        end = kwargs.get('end', '\n')
        file = kwargs.get('file', sys.stdout)
        _real_print(*objects, sep=sep, end=end, file=file)
        if kwargs.get('flush', False):
            file.flush()
else:
    from builtins import print


if PY2:
    input = raw_input
    try:
        from cStringIO import StringIO
    except ImportError:
        from StringIO import StringIO
else:
    from builtins import input
    from io import StringIO


__all__ = ['PY2', 'PY3', 'input', 'print', 'queue', 'StringIO']
