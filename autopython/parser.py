# -*- coding: utf-8 -*-

import codecs
import codeop
import io
import os
import re
import sys

from collections import namedtuple
from .compat import PY2

ENCODING_RE = re.compile(('' if PY2 else '(?a)') +
                         r'^[ \t\f]*#.*coding[:=][ \t]*([-\w.]+)')

StatementInfo = namedtuple('StatementInfo',
                           'line_number statement prompts first_line code')


def parse_file(filename):
    compiler = codeop.CommandCompiler()

    source_lines = read_source_code(filename)
    source_lines, line_number = strip_encoding_declaration(source_lines)

    statements = []
    statement = ''
    prompts = []
    statement_started = False
    statement_first_line = statement_current_line = -1
    statement_line_number = line_number

    for line in source_lines:
        line_number += 1
        statement_current_line += 1

        prompts.append('ps2' if statement_started else 'ps1')
        statement += line

        is_empty_line = line.strip() == ''
        statement_started = statement_started or not is_empty_line

        if statement_first_line == -1:
            if line.startswith('#'):
                continue
            elif is_empty_line:
                statement_started = False
                continue
            else:
                statement_first_line = statement_current_line
                statement_line_number = line_number

        code, compiled = compile_statement(compiler, statement)
        if compiled:
            statements.append(StatementInfo(statement_line_number, statement,
                              prompts, statement_first_line, code))
            statement_started = False
            statement_current_line = statement_first_line = -1
            statement = ''
            prompts = []

    if statement:
        if prompts[-1] == 'ps2':
            statement += '\n'
            prompts.append('ps2')
        code, compiled = compile_statement(compiler, statement)
        statements.append(StatementInfo(statement_line_number, statement,
                          prompts, statement_first_line, code))
    return statements


def read_source_code(filename):
    with open(filename, 'rUb') as source_file:
        stripped_source = source_file.read().rstrip() + b'\n'
        source_lines = stripped_source.splitlines()

    if not source_lines:
        return source_lines

    encoding = 'utf-8'
    bom_found = source_lines[0].startswith(codecs.BOM_UTF8)
    if bom_found:
        source_lines[0] = source_lines[0][len(codecs.BOM_UTF8):]

    for line in source_lines[:2]:
        try:
            # If the line is an encoding declaration, it must be ASCII.
            # If is not, it must be UTF-8 (the default encoding).
            # Either way, it should be possible to decoded it as UTF-8.
            line = line.decode('utf-8')
        except UnicodeDecodeError:
            raise SyntaxError('invalid or missing encoding declaration')

        result = ENCODING_RE.match(line)
        if result:
            try:
                codec = codecs.lookup(result.group(1))
            except LookupError:
                raise SyntaxError('unknown encoding: ' + result.group(1))

            encoding = codec.name
            if bom_found and encoding != 'utf-8':
                raise SyntaxError('encoding problem: utf-8')
            break

    output_encoding = sys.stdout.encoding
    source_code = []
    for line in source_lines:
        try:
            decoded_line = (line + b'\n').decode(encoding)
        except UnicodeDecodeError as exp:
            msg = "'{}' codec can't decode byte on line {}, column {}".format(
                exp.encoding, len(source_code) + 1, exp.start)
            raise SyntaxError(msg)

        try:
            # To test if the line can be printed on the console
            decoded_line.encode(output_encoding)
        except UnicodeEncodeError as exp:
            msg = "the byte on line {}, column {} can't be printed " \
                "(maybe using the wrong encoding '{}'?)".format(
                len(source_code) + 1, exp.start + 1, encoding)
            raise SyntaxError(msg)

        source_code.append(decoded_line)

    return source_code


def strip_encoding_declaration(source_lines):
    lines_stripped = 0
    if source_lines and source_lines[0].startswith('#!'):
        source_lines = source_lines[1:]
        lines_stripped += 1

    if source_lines and ENCODING_RE.match(source_lines[0]):
        source_lines = source_lines[1:]
        lines_stripped += 1

    while source_lines and not source_lines[0].strip():
        source_lines = source_lines[1:]
        lines_stripped += 1

    return source_lines, lines_stripped


def compile_statement(compiler, source):
    if source.endswith('\n'):
        source = source[:-1]
    if PY2:
        source = source.encode(sys.stdin.encoding)
    try:
        code = compiler(source, filename='<stdin>', symbol='single')
        compiled = code is not None
    except (OverflowError, SyntaxError, ValueError):
        compiled = True
        code = None
    return code, compiled
