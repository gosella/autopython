# -*- coding: utf-8 -*-

from __future__ import print_function

import random
import signal
import time

from . import console, highlighter as hl
from .compat import input, print


def layout_code(lexer, statement, prompts, index_number=None, index_line=-1,
                console_width=-1, console_height=-1):
    size = console.get_terminal_size()
    if console_width < 1:
        console_width = size.columns - 1
    if console_height < 1:
        console_height = size.lines - 1

    if index_number is None or index_line < 0:
        index_str = ''
    else:
        index_str = '  ({})'.format(index_number)

    max_line = statement.count('\n')
    line = 0
    col = 0
    iter_prompts = iter(prompts)
    for _, ttype, value in lexer.get_tokens_unprocessed(statement):
        if col == 0:
            prompt, prompt_len = next(iter_prompts)
            yield line, 0, None, '\r' + prompt, False
            col = prompt_len
            width = console_width - col
            if line == index_line:
                width -= len(index_str)
                yield line, col, None, ' ' * width, False
                yield line, col + width, hl.Token.Index, index_str, False
            yield line, 0, None, '\r' + prompt, False
        if value == '':
            continue
        elif value == '\n':
            line += 1
            col = 0
            if line == max_line:
                break
            yield line, col, None, '\n', False
        else:
            new_col = col + len(value)
            while new_col > width:
                extra = new_col - width
                yield line, col, ttype, value[:-extra], True
                yield line, new_col - extra, None, '\n', False
                value = value[-extra:]
                col = 0
                new_col = len(value)
                width = console_width

            yield line, col, ttype, value, True
            col = new_col


def simulate_typing(tokens, color_scheme=None, typing_delay=30):
    colorize = hl.HAVE_HIGHLIGHTING and color_scheme is not None
    delay = typing_delay / 1000.0
    current_line = 0
    prev_sigint_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)
    try:
        console.disable_echo()
        for line, col, ttype, text, type_it in tokens:
            if line != current_line:
                yield current_line
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

        yield current_line
    finally:
        signal.signal(signal.SIGINT, prev_sigint_handler)
        console.enable_echo()


def ask_index(max_index, color_scheme=None):
    def colored(color, text):
        return hl.ansiformat(color, text) if color_scheme else text
    try:
        text = input(colored('*green*', '\n\nEnter new index: ')).strip()
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
