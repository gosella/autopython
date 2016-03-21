#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import code
import colorama
import console
import io
import os
import random
import script_parser
import sys
import time

from datetime import datetime

from pygments import highlight
from pygments.token import Token
from pygments.lexers import PythonConsoleLexer, Python3TracebackLexer
from pygments.console import ansiformat
from pygments.formatters import TerminalFormatter

colorama.init()

TERMINAL_COLORS = {
    Token:                        '',

    Token.Text:                   '',
    Token.Whitespace:             'lightgray',
    Token.Error:                  '_red_',
    Token.Other:                  '',

    Token.Comment:                'darkgray',
    Token.Comment.Multiline:      '',
    Token.Comment.Preproc:        'teal',
    Token.Comment.Single:         '',
    Token.Comment.Special:        '',

    Token.Keyword:                'turquoise',
    Token.Keyword.Constant:       '',
    Token.Keyword.Declaration:    '',
    Token.Keyword.Namespace:      '',
    Token.Keyword.Pseudo:         '',
    Token.Keyword.Reserved:       '',
    Token.Keyword.Type:           'teal',

    Token.Operator:               'fuchsia',
    Token.Operator.Word:          'purple',

    Token.Punctuation:            '',

    Token.Name:                   '**',
    Token.Name.Attribute:         '',
    Token.Name.Builtin:           'teal',
    Token.Name.Builtin.Pseudo:    '',
    Token.Name.Class:             '*darkgreen*',
    Token.Name.Constant:          '',
    Token.Name.Decorator:         '',
    Token.Name.Entity:            '',
    Token.Name.Exception:         'teal',
    Token.Name.Function:          'darkgreen',
    Token.Name.Property:          '',
    Token.Name.Label:             '',
    Token.Name.Namespace:         '*yellow*',
    Token.Name.Other:             '',
    Token.Name.Tag:               'blue',
    Token.Name.Variable:          '',
    Token.Name.Variable.Class:    '',
    Token.Name.Variable.Global:   '',
    Token.Name.Variable.Instance: '',

    Token.Number:                 'blue',
    Token.Number.Float:           '',
    Token.Number.Hex:             '',
    Token.Number.Integer:         '',
    Token.Number.Integer.Long:    '',
    Token.Number.Oct:             '',

    Token.Literal:                '',
    Token.Literal.Date:           '',

    Token.String:                 'yellow',
    Token.String.Backtick:        '',
    Token.String.Char:            '',
    Token.String.Doc:             '',
    Token.String.Double:          '',
    Token.String.Escape:          '',
    Token.String.Heredoc:         '',
    Token.String.Interpol:        '',
    Token.String.Other:           '',
    Token.String.Regex:           '',
    Token.String.Single:          '',
    Token.String.Symbol:          '',

    Token.Generic:                '',
    Token.Generic.Deleted:        'red',
    Token.Generic.Emph:           '',
    Token.Generic.Error:          'red',
    Token.Generic.Heading:        '**',
    Token.Generic.Inserted:       'darkgreen',
    Token.Generic.Output:         '',
    Token.Generic.Prompt:         'lightgray',
    Token.Generic.Strong:         '**',
    Token.Generic.Subheading:     '*purple*',
    Token.Generic.Traceback:      '',
}


class PresenterInterpreter(code.InteractiveInterpreter):
    def compilesource(self, source, filename='<stdin>', symbol='single'):
        try:
            code = self.compile(source, filename, symbol)
        except (OverflowError, SyntaxError, ValueError):
            self.showsyntaxerror(filename)
            return False, None

        return code is None, code


class HighlightingInterpreter(PresenterInterpreter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._lexer = Python3TracebackLexer()
        colorscheme = {token: (color, color) for token, color in TERMINAL_COLORS.items()}
        self._formatter = TerminalFormatter(colorscheme=colorscheme)


    def highlight_error(self, method, *args, **kwargs):
        new_stderr = io.StringIO()
        old_stderr, sys.stderr = sys.stderr, new_stderr
        try:
            method(*args, **kwargs)
        finally:
            sys.stderr = old_stderr
        output = new_stderr.getvalue()
        sys.stderr.write(highlight(output, self._lexer, self._formatter))
        sys.stderr.flush()


    def showtraceback(self):
        self.highlight_error(super().showtraceback)


    def showsyntaxerror(self, filename):
        self.highlight_error(super().showsyntaxerror, filename)


def lower_upper_key(char):
    return (char.lower(), char.upper())


class Presenter(object):
    READY_TO_TYPE, READY_TO_EXECUTE, READY_TO_FAIL = range(3)

    KEY_PREV = (console.PGUP,) + lower_upper_key('p')
    KEY_NEXT = (console.PGDN, ' ', '\n', '\r')
    KEY_AGAIN = lower_upper_key('r')
    KEY_GOTO = lower_upper_key('g')
    KEY_SHELL = lower_upper_key('s')
    KEY_EXIT = lower_upper_key('q')


    def __init__(self, filename, output=None, width=80, colors=True,
                 animation=True, typing_delay=40, logging=False):
        if output is None:
            self.output = sys.stdout
        else:
            self.output = output

        self.logging = logging
        if logging:
            time = datetime.now().strftime('-%Y-%m-%d')
            log_name = os.path.splitext(filename)[0] + time + '.log'
            self.logger = open(log_name, 'at')
            self.logger.write('\n')
            bar = '=' * 34
            self.log(bar, '=====  AutoPython initiated  =====', bar)

        self.colors = colors
        self.animation = animation
        self.typing_delay = typing_delay

        self.lexer = PythonConsoleLexer(python3=True)
        self.width = self.current_width = width - 1
        
        self.ps1 = self.hl_ps1 = '>>> '
        self.ps2 = self.hl_ps2 = '... '

        self.colorscheme = TERMINAL_COLORS
        if self.colors:
            self.hl_ps1 = ansiformat(self.colorscheme[Token.Generic.Prompt], self.ps1)
            self.hl_ps2 = ansiformat(self.colorscheme[Token.Generic.Prompt], self.ps2)

        self.reset_interpreter()
        self.load_file(filename)


    def reset_interpreter(self):
        self.interpreter = HighlightingInterpreter() if self.colors else PresenterInterpreter()
        self.ns = self.interpreter.locals
        self.ns.update(PRESENTER=self)
        self._code_to_execute = None
        self._code_to_fail = None
        self.state = Presenter.READY_TO_TYPE
        self.index = 0


    def load_file(self, filename):
        self.statements = script_parser.parse_file(filename)


    def log(self, message, *rest):
        if self.logging:
            timestamp = datetime.now().strftime('[%Y-%m-%d %H:%M:%S]')
            print(timestamp, message, file=self.logger)
            indent = ' ' * len(timestamp)
            for line in rest:
                print(indent, line.rstrip(), file=self.logger)


    def begin(self):
        cprt = 'Type "help", "copyright", "credits" or "license" for more information.'
        self.write('Python %s on %s\n%s\n' % (sys.version, sys.platform, cprt))
        self.index = 0
        self.prompt()
        self.log('In the beginning...')


    def prompt(self):
        self.write(self.hl_ps1)
        self.state = Presenter.READY_TO_TYPE


    def cancel(self):
        self.write(' ^C\n', ansiformat('*red*', 'KeyboardInterrupt') if self.colors else 'KeyboardInterrupt', '\n')
        self.prompt()


    def end(self):
        if self.state != Presenter.READY_TO_TYPE:
            self.cancel()
        self.show_code((self.ps1, 'exit()'))
        self.write('\n')

        if self.logging:
            pending = len(self.statements) - self.index
            if pending > 0:
                reason = 'Quiting with {} more statement{} to go.'.format(pending, 's' if pending > 1 else '')
            else:
                reason = 'The End.'

            self.log(reason)
            self.logger.close()


    def prev(self):
        if self.index > 1 or (self.index == 1 and self.state == Presenter.READY_TO_TYPE):
            if self.state != Presenter.READY_TO_TYPE:
                self.cancel()
                self.index -= 2
            else:
                self.index -= 1

            self.log('Going back to previous statement.')
            return self.next()
        else:
            return self.index < len(self.statements)


    def next(self):
        if self.state == Presenter.READY_TO_TYPE and self.index < len(self.statements):
            line_number, statement, lines, statement_first_line, code = self.statements[self.index]
            self.index += 1
            self.log('On statement {} (line {}):'.format(self.index, line_number), *statement.splitlines())
            self.show_code(lines, self.index, statement_first_line)

            if code is None:
                self._code_to_fail = statement
                self.state = Presenter.READY_TO_FAIL
            else:
                self._code_to_execute = code
                self.state = Presenter.READY_TO_EXECUTE

        elif self.state == Presenter.READY_TO_EXECUTE:
            line_number, *_ = self.statements[self.index-1]
            self.log('Executing statement {} (line {}):'.format(self.index, line_number))
            
            self.write('\n')
            if self._code_to_execute is not None:
                self.interpreter.runcode(self._code_to_execute)
                self._code_to_execute = None
            self.prompt()

        elif self.state == Presenter.READY_TO_FAIL:
            line_number, *_ = self.statements[self.index-1]
            self.log('Raising exception on statement {} (line {}):'.format(self.index, line_number))
            
            self.write('\n')
            if self._code_to_fail is not None:
                self.interpreter.compilesource(self._code_to_fail)
                self._code_to_fail = None
            self.prompt()

        return self.state != Presenter.READY_TO_TYPE or self.index < len(self.statements)


    def go_to(self, n):
        if self.state != Presenter.READY_TO_TYPE:
            self.next()

        if n < 0:
            n = len(self.statements) + n + 1


        if 1 <= n <= len(self.statements):
            self.log('Jumping to statement {} (line {}).'.format(n, self.statements[n-1][0]))

            n -= 1
            if n < self.index:
                self.reset_interpreter()
            elif self.state != Presenter.READY_TO_TYPE:
                self.next()

            if n > 0:
                old_anim = self.animation
                self.animation = False
                try:
                    while self.index < n:
                        self.next()
                    self.next()
                finally:
                    self.animation = old_anim

        return self.next()


    def interact(self):
        if self.state != Presenter.READY_TO_TYPE:
            self.cancel()
        self.write('\r')

        self.log('Entering interactive mode.')

        if self.colors:
            ps1 = ansiformat('*green*', self.ps1)
            ps2 = ansiformat('*green*', self.ps2)
        else:
            ps1 = self.ps1
            ps2 = self.ps2

        lines = []
        need_more = False
        while True:
            try:
                try:
                    self.write(ps2 if need_more else ps1)
                    line = input()
                    lines.append(line)
                except EOFError:
                    break
                else:
                    source = '\n'.join(lines)
                    need_more = self.interpreter.runsource(source)
                    if not need_more:
                        self.log('Executing new statement:', *lines)
                        lines = []
            except KeyboardInterrupt:
                self.write('\n', ansiformat('*red*', 'KeyboardInterrupt') if self.colors else 'KeyboardInterrupt', '\n')
                lines = []
                need_more = False

        self.log('Leaving interactive mode.')
        self.write('\r', self.hl_ps1)


    def write(self, text, *more_text):
        self.output.write(text)
        for t in more_text:
            self.output.write(t)
        self.output.flush()


    def show_code(self, code, index=None, index_line=-1):
        index_str = '  ({})'.format(index) if index_line >= 0 else ''
        default_width = self.width
        reduced_width = default_width - len(index_str)

        def process_code():
            line = col = 0
            if index_line == 0:
                width = reduced_width
            else:
                width = default_width
                yield line, col, Token.Text, '\r'

            for ttype, value in self.lexer.get_tokens(''.join(code)):
                if value == '':
                    continue
                elif value == '\n':
                    yield line, col, ttype, value

                    line += 1
                    col = 0
                    width = reduced_width if line == index_line else default_width
                else:
                    new_col = col + len(value)
                    while new_col > width:
                        extra = new_col - width
                        yield line, col, ttype, value[:-extra]
                        yield line, new_col - extra, Token.Text, '\n'
                        value = value[-extra:]
                        col = 0
                        new_col = len(value)
                        width = default_width

                    yield line, col, ttype, value
                    col = new_col

        def add_index_and_animations(tokens):
            index_not_shown = True
            for line, col, ttype, value in tokens:
                if index_not_shown and line == index_line:
                    blanks = ' ' * (reduced_width - col)
                    if line == 0:
                        blanks = blanks[:-4]
                    if blanks:
                        yield Token.Text, blanks, line, False
                    yield Token.Generic.Strong, index_str, line, False
                    yield Token.Text, '\r', line, False
                    index_not_shown = False

                anim = not (ttype is Token.Generic.Prompt or
                            (len(value) > 1 and value.isspace()))
                yield ttype, value, line, anim

        def strip_last_newline(tokens):
            iterator = iter(tokens)
            last = next(iterator)
            for token in iterator:
                yield last
                last = token
            if last[1] != '\n':
                yield last

        def colorize(tokens):
            if self.colors:
                for ttype, value, line, anim in tokens:
                    while ttype:
                        color = self.colorscheme.get(ttype)
                        if color:
                            yield value, line, anim, color
                            break
                        ttype = ttype[:-1]
                    else:
                        yield value, line, anim, None
            else:
                for ttype, value, line, anim in tokens:
                    yield value, line, anim, None

        def show(tokens):
            anim = self.animation
            delay = self.typing_delay / 1000

            for text, line, simulate_typing, color in tokens:
                if color is not None:
                    on, off = ansiformat(color, '|').split('|')
                    self.write(on)

                if anim and simulate_typing:
                    for char in text:
                        self.write(char)
                        if not char.isspace():
                            time.sleep(delay * (0.5 + random.random()))
                else:
                    self.write(text)

                if color is not None:
                    self.write(off)

        console.disable_echo()
        show(colorize(strip_last_newline(add_index_and_animations(process_code()))))
        console.enable_echo()


    def run(self):
        try:
            self.begin()

            more_sentences = True
            while True:
                key = console.getch()
                # print('Key code:', repr(key))
                if key in Presenter.KEY_PREV:
                    more_sentences = self.prev()

                elif key in Presenter.KEY_NEXT:
                    if more_sentences:
                        more_sentences = self.next()
                    else:
                        break

                elif key in Presenter.KEY_AGAIN:
                    more_sentences = self.again()

                elif key in Presenter.KEY_GOTO:
                    if self.state != Presenter.READY_TO_TYPE:
                        self.next()

                    try:
                        self.write('\n\n')
                        if self.colors:
                            self.write(colorama.Fore.GREEN, colorama.Style.BRIGHT)
                        self.write('Go to: ')
                        sentence = input()
                    finally:
                        if self.colors:
                            self.write(colorama.Style.RESET_ALL)
                        self.write('\n')
                        self.prompt()

                    try:
                        more_sentences = self.go_to(int(sentence))
                    except ValueError:
                        pass

                elif key in Presenter.KEY_SHELL:
                    self.interact()

                elif key in Presenter.KEY_EXIT:
                    break

            self.end()
        finally:
            if self.colors:
                self.write(colorama.Style.RESET_ALL)


if __name__ == '__main__':
    presenter = Presenter(sys.argv[1], width=console.getwidth(),
                          colors=True, animation=True, logging=True)
    presenter.run()
