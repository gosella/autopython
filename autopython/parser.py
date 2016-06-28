# -*- coding: utf-8 -*-

import codecs
import codeop
import io
import os
import re
import sys

from collections import namedtuple

PY2 = sys.version_info[0] == 2
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
        code, compiled = compile_statement(compiler, statement)
        statements.append(StatementInfo(statement_line_number, statement,
                          prompts, statement_first_line, code))
    return statements


def read_source_code(filename):
    with open(filename, 'rb') as source_file:
        source_bytes = source_file.read()

    encoding = 'utf-8'
    bom_found = source_bytes.startswith(codecs.BOM_UTF8)
    if bom_found:
        source_bytes = source_bytes[len(codecs.BOM_UTF8):]

    first_lines = source_bytes.split(os.linesep.encode('utf-8'), 2)[:2]
    for line in first_lines:
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

    newline_decoder = io.IncrementalNewlineDecoder(None, translate=True)
    try:
        source_code = newline_decoder.decode(source_bytes.decode(encoding))
        return source_code.splitlines(True)
    except UnicodeDecodeError as exp:
        line = 1 + source_bytes[:exp.end].count(b'\n')
        last_n = 1 + source_bytes[:exp.end].rfind(b'\n')
        column = exp.start - last_n + 1
        msg = "'{}' codec can't decode byte on line {}, column {}".format(
            exp.encoding, line, column)
        raise SyntaxError(msg)


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
    try:
        code = compiler(source, filename='<stdin>', symbol='single')
        compiled = code is not None
    except (OverflowError, SyntaxError, ValueError):
        compiled = True
        code = None
    return code, compiled
