#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import codeop
import io
import re
import tokenize

def parse_file(filename, ps1=None, ps2=None):
    if ps1 is None: ps1 = '>>> '
    if ps2 is None: ps2 = '... '

    compiler = codeop.CommandCompiler()

    source_lines = read_source_code(filename)
    source_lines, line_number = strip_encoding_declaration(source_lines)

    statements = []
    statement = ''
    output_lines = []
    statement_started = False
    statement_first_line = statement_current_line = -1
    statement_line_number = line_number

    for line in source_lines:
        line_number += 1
        statement_current_line += 1

        if not statement_started:
            output_lines.append(ps1 + line)
        else:
            output_lines.append(ps2 + line)

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

        if statement_started:
            statement += line

        code, compiled = compile_statement(compiler, statement)
        if compiled:
            statements.append((statement_line_number, statement, output_lines,
                               statement_first_line, code))
            statement_started = False
            statement_current_line = statement_first_line = -1
            statement = ''
            output_lines = []

    if statement:
        code, compiled = compile_statement(compiler, statement)
        statements.append((statement_line_number, statement, output_lines,
                           statement_first_line, code))

    return statements


def read_source_code(filename):
    with open(filename, 'rb') as source_file:
        encoding, first_lines = tokenize.detect_encoding(source_file.readline)
        source_bytes = b''.join(first_lines) + source_file.read()

    newline_decoder = io.IncrementalNewlineDecoder(None, translate=True)
    source_code = newline_decoder.decode(source_bytes.decode(encoding))
    return source_code.splitlines(True)


ENCODING_RE = re.compile(r'^[ \t\f]*#.*coding[:=][ \t]*([-\w.]+)', re.ASCII)


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
