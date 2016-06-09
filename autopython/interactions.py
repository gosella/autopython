import random
import signal
import time

from . import console, highlighter as hl


def simulate_typing(statement, prompts, index_number=None, index_line=-1,
                    color_scheme=None, typing_delay=30,
                    console_width=-1, console_height=-1,
                    lexer=hl.LineLexer()):
    if console_width < 1:
        console_width = console.get_width() - 1

    if console_height < 1:
        console_height = console.get_height() - 1

    def tokenize():
        iter_prompts = iter(prompts)
        lines = statement.splitlines()
        max_line = len(lines) - 1

        if index_number is None or index_line < 0:
            index_str = ''
        else:
            index_str = '  ({})'.format(index_number)

        line = 0
        col = 0
        for _, ttype, value in lexer.get_tokens_unprocessed(statement):
            if col == 0:
                prompt, prompt_len = next(iter_prompts)
                yield line, col, '\r' + prompt, False, None
                col = prompt_len
                width = console_width - col
                if line == index_line:
                    width -= len(index_str)
                    yield line, col, ' ' * width, False, None
                    color = hl.get_color_for(hl.Token.Index, color_scheme)
                    yield line, col + width, index_str, False, color
                yield line, 0, '\r' + prompt, False, None
            if value == '':
                continue
            elif value == '\n':
                if line == max_line:
                    break

                line += 1
                col = 0
                yield line, col, '\n', False, None
            else:
                color = hl.get_color_for(ttype, color_scheme)
                new_col = col + len(value)
                while new_col > width:
                    extra = new_col - width
                    yield line, col, value[:-extra], True, color
                    yield line, new_col - extra, '\n', False, None
                    value = value[-extra:]
                    col = 0
                    new_col = len(value)
                    width = console_width

                yield line, col, value, True, color
                col = new_col

    current_line = 0
    delay = typing_delay / 1000
    colorize = hl.HAVE_HIGHLIGHTING and color_scheme is not None
    color = None

    prev_sigint_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)
    try:
        console.disable_echo()
        for line, col, text, type_it, color in tokenize():
            if line != current_line:
                yield current_line
                current_line = line

            if colorize and color:
                color_on, color_off = hl.ansiformat(color, '|').split('|')
                print(end=color_on)

            if typing_delay and type_it:
                for char in text:
                    print(end=char, flush=True)
                    if not char.isspace():
                        time.sleep(delay * (0.5 + random.random()))
            else:
                print(end=text, flush=True)

            if colorize and color:
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
    except ValueError:
        new_index = None
        print(colored('*red*', 'Invalid index:'), repr(text), '\n'
              'Only indexes from 1 to {0} (or from -{0} to -1) '
              'are allowed.'.format(max_index))
    except KeyboardInterrupt:
        new_index = None
        print(colored('*red*', '\nKeyboardInterrupt'))
    print(flush=True)
    return new_index
