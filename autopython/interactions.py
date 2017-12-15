# -*- coding: utf-8 -*-

from __future__ import print_function

import random
import signal
import time

from . import console, highlighter as hl
from .compat import input, print
from .highlighter import Token


def _tokenize(lexer, statement):
    for _, ttype, text in lexer.get_tokens_unprocessed(statement):
        if ttype == Token.Literal.String.Doc:
            for line in text.splitlines(keepends=True):
                if line.endswith('\n'):
                    yield ttype, line[:-1]
                    yield Token.Text, '\n'
                else:
                    yield ttype, line
        else:
            yield ttype, text


def layout_code(lexer, statement, prompts, index_number=None, index_line=-1,
                scroll_context_lines=1, console_width=-1, console_height=-1):
    # This generator yields a tuple containing:
    #  - line and column number
    #  - The type of the text
    #  - The text
    #  - A flag telling if the text should be typed.
    #  - A flag indicating that the console screen is completely filled.
    size = console.get_terminal_size()
    if console_width < 1:
        console_width = size.columns - 1
    if console_height < 1:
        console_height = size.lines

    if index_number is None or index_line < 0:
        index_str = ''
    else:
        index_str = '  ({})'.format(index_number)

    max_line = statement.count('\n')
    displayed_line = 0
    display_limit = console_height
    line = 0
    col = 0
    iter_prompts = iter(prompts)
    for ttype, text in _tokenize(lexer, statement):
        if col == 0:
            prompt, prompt_len = next(iter_prompts)
            yield line, 0, None, '\r' + prompt, False, False
            col = prompt_len
            width = console_width - col
            if line == index_line:
                width -= len(index_str)
                yield line, col, None, ' ' * width, False, False
                yield line, col + width, hl.Token.Index, index_str, False, False
            yield line, 0, None, '\r' + prompt, False, False
        if text == '':
            continue
        elif text == '\n':
            line += 1
            if line == max_line:
                break
            col = 0
            displayed_line += 1
            is_full = displayed_line == display_limit
            if is_full:
                displayed_line = 0
                display_limit = console_height - scroll_context_lines
            yield line, col, None, '\n', False, is_full
        else:
            new_col = col + len(text)
            while new_col > width:
                extra = new_col - width
                yield line, col, ttype, text[:-extra], True, False
                displayed_line += 1
                is_full = displayed_line == display_limit
                if is_full:
                    displayed_line = 0
                    display_limit = console_height - scroll_context_lines
                yield line, new_col - extra, None, '\n', False, is_full
                text = text[-extra:]
                col = 0
                new_col = len(text)
                width = console_width

            yield line, col, ttype, text, True, False
            col = new_col


def simulate_typing(tokens, color_scheme=None, typing_delay=30):
    colorize = hl.HAVE_HIGHLIGHTING and color_scheme is not None
    delay = typing_delay / 1000.0
    current_line = 0
    prev_sigint_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)
    try:
        console.disable_echo()
        for line, _, ttype, text, type_it, console_filled in tokens:
            if line != current_line or console_filled:
                yield current_line, console_filled
                current_line = line

            if colorize and ttype:
                color = hl.get_color_for(ttype, color_scheme)
                color_on, color_off = hl.ansiformat(color, '|').split('|')
                print(end=color_on)

            if delay and type_it:
                for char in text:
                    print(end=char, flush=True)
                    if not char.isspace():
                        time.sleep(delay * (0.5 + random.random()))
            else:
                print(end=text, flush=True)

            if colorize and ttype:
                print(end=color_off)

        yield current_line, False
    finally:
        signal.signal(signal.SIGINT, prev_sigint_handler)
        console.enable_echo()


def ask_index(max_index, color_scheme=None):
    def colored(color, text):
        return hl.ansiformat(color, text) if color_scheme else text
    try:
        print(end=colored('*green*', '\n\nEnter new index: '))
        text = input().strip()
        if text:
            new_index = int(text)
            if new_index == 0 or abs(new_index) > max_index:
                raise ValueError
            if new_index < 0:
                new_index = max_index + new_index + 1
            new_index -= 1
        else:
            new_index = None
    except EOFError:
        new_index = None
        print('Canceling')
    except ValueError:
        new_index = None
        print(colored('*red*', 'Invalid index:'), repr(text),
              '(only indexes from 1 to {0} (or from -{0} to -1) '
              'are allowed).'.format(max_index))
    except KeyboardInterrupt:
        new_index = None
        print(colored('*red*', '\nKeyboardInterrupt'))
    print(flush=True)
    return new_index
