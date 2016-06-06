# -*- coding: utf-8 -*-

import io
import sys

from code import InteractiveInterpreter
from .highlighter import HAVE_HIGHLIGHTING
from .highlighter import highlight, ansiformat, get_color_for, COLOR_SCHEMES
from .highlighter import Token, TerminalFormatter, Python3Lexer, TracebackLexer
from .interactions import simulate_typing, ask_index


class PresenterInterpreter(InteractiveInterpreter):
    def compilesource(self, source, filename='<stdin>', symbol='single'):
        try:
            code = self.compile(source, filename, symbol)
        except (OverflowError, SyntaxError, ValueError):
            self.showsyntaxerror(filename)
            return False, None
        return code is None, code


class HighlightingInterpreter(PresenterInterpreter):
    def __init__(self, *args, **kwargs):
        scheme = COLOR_SCHEMES.get(kwargs.pop('color_scheme', 'default'), {})
        super().__init__(*args, **kwargs)
        self._lexer = TracebackLexer()
        colors = {token: (color, color) for token, color in scheme.items()}
        self._formatter = TerminalFormatter(colorscheme=colors)

    def highlight_error(self, method, *args, **kwargs):
        new_stderr = io.StringIO()
        old_stderr, sys.stderr = sys.stderr, new_stderr
        try:
            method(*args, **kwargs)
        finally:
            sys.stderr = old_stderr
        output = new_stderr.getvalue()
        print(end=highlight(output, self._lexer, self._formatter),
              file=sys.stderr, flush=True)

    def showtraceback(self):
        self.highlight_error(super().showtraceback)

    def showsyntaxerror(self, filename=None):
        self.highlight_error(super().showsyntaxerror, filename)


class PresenterShell(object):
    def __init__(self, color_scheme='default', use_ipython=False):
        self._color_scheme = color_scheme
        self._use_ipython = use_ipython
        self._interpreter = None
        self._hl_ps1 = self._ps1 = '>>> '
        self._hl_ps2 = self._ps2 = '... '
        if color_scheme:
            color = get_color_for(Token.Generic.Prompt, color_scheme)
            self._hl_ps1 = ansiformat(color, self._ps1)
            self._hl_ps2 = ansiformat(color, self._ps2)
            self._lexer = Python3Lexer()

    def _colored(self, color, text):
        return ansiformat(color, text) if self._color_scheme else text

    def reset_interpreter(self):
        if self._use_ipython:
            from IPython.terminal.interactiveshell import \
                TerminalInteractiveShell

            class IPythonInterpreter(TerminalInteractiveShell,
                                     PresenterInterpreter):
                pass

            self._interpreter = IPythonInterpreter(confirm_exit=False)
            if not HAVE_HIGHLIGHTING or not self._color_scheme:
                self._interpreter.run_line_magic('colors', 'NoColor')
            # Customize IPython to make it look like the CPYthon shell
            self._interpreter.prompt_manager.in_template = self._ps1
            self._interpreter.prompt_manager.in2_template = self._ps2
            self._interpreter.prompt_manager.out_template = ''
            self._interpreter.prompt_manager.justify = False
            self._interpreter.separate_in = ''
        elif HAVE_HIGHLIGHTING and self._color_scheme:
            self._interpreter = HighlightingInterpreter(
                color_scheme=self._color_scheme)
        else:
            self._interpreter = PresenterInterpreter()

    def begin(self):
        self.reset_interpreter()
        print('AutoPython {} on {}'.format(sys.version, sys.platform),
              'Type "help", "copyright", "credits" or "license" '
              'for more information.', self._hl_ps1,
              sep='\n', end='', flush=True)

    def control_c(self):
        print('^C', self._colored('*red*', 'KeyboardInterrupt'),
              self._hl_ps1, sep='\n', end='', flush=True)

    def show(self, statement, prompts, index=None, index_line=-1,
             typing_delay=0):
        ps1 = self._hl_ps1, len(self._ps1)
        ps2 = self._hl_ps2, len(self._ps2)
        hl_prompts = (ps1 if p == 'ps1' else ps2 for p in prompts)
        for _ in simulate_typing(statement, hl_prompts, index, index_line,
                                 color_scheme=self._color_scheme,
                                 typing_delay=typing_delay,
                                 lexer=self._lexer):
            pass

    def execute(self, statement, code=None):
        print(flush=True)
        if code is not None:
            self._interpreter.runcode(code)
        else:
            self._interpreter.compilesource(statement)
        print(end=self._hl_ps1, flush=True)

    def interact(self):
        print(flush=True)
        if self._use_ipython:
            self._interpreter.history_manager.reset(True)
            self._interpreter.interact()
            history = map(str.splitlines,
                          self._interpreter.history_manager.input_hist_raw)
        else:
            ps1 = self._colored('*green*', self._ps1)
            ps2 = self._colored('*green*', self._ps2)
            lines = []
            history = []
            need_more = False
            print(end='\r', flush=True)
            while True:
                try:
                    try:
                        print(end=ps2 if need_more else ps1, flush=True)
                        line = input()
                        lines.append(line)
                    except EOFError:
                        break
                    else:
                        source = '\n'.join(lines)
                        need_more = self._interpreter.runsource(source)
                        if not need_more:
                            history.append(lines)
                            lines = []
                except KeyboardInterrupt:
                    print(self._colored('*red*', '\nKeyboardInterrupt'),
                          flush=True)
                    lines = []
                    need_more = False
            print(flush=True)
        print(end=self._hl_ps1, flush=True)
        return history

    def ask_where_to_go(self, max_index):
        new_index = ask_index(max_index, self._color_scheme)
        print(end=self._hl_ps1, flush=True)
        return new_index

    def quit(self):
        self.show('quit()', ['ps1'], typing_delay=30)

    def end(self):
        print(flush=True)
