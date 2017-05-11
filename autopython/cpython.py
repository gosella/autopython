# -*- coding: utf-8 -*-

from __future__ import print_function

import sys

from code import InteractiveInterpreter
from threading import Thread
from .compat import PY2, input, print, queue, StringIO
from .highlighter import HAVE_HIGHLIGHTING, highlight, ansiformat, Token
from .highlighter import TerminalFormatter, get_color_for, COLOR_SCHEMES
from .highlighter import Python3Lexer, TracebackLexer, LineLexer
from .interactions import layout_code, simulate_typing, ask_index


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
        PresenterInterpreter.__init__(self, *args, **kwargs)
        self._lexer = TracebackLexer()
        colors = {token: (color, color) for token, color in scheme.items()}
        self._formatter = TerminalFormatter(colorscheme=colors)

    def highlight_error(self, method, *args, **kwargs):
        new_stderr = StringIO()
        old_stderr, sys.stderr = sys.stderr, new_stderr
        try:
            method(self, *args, **kwargs)
        finally:
            sys.stderr = old_stderr
        output = new_stderr.getvalue()
        print(end=highlight(output, self._lexer, self._formatter),
              file=sys.stderr, flush=True)

    def showtraceback(self):
        self.highlight_error(PresenterInterpreter.showtraceback)

    def showsyntaxerror(self, filename=None):
        self.highlight_error(PresenterInterpreter.showsyntaxerror, filename)


class Quitter(object):
    def __init__(self, shell, func):
        self.__shell = shell
        self.__func = func

    def __call__(self):
        if self.__shell._interacting:
            self.__shell._interacting = False
        else:
            return self.__func()

    def __repr__(self):
        return repr(self.__func)


class PresenterShell(object):
    def __init__(self, color_scheme='default', use_ipython=False):
        self._color_scheme = color_scheme
        self._use_ipython = use_ipython
        self._interpreter = None
        self._hl_ps1 = self._ps1 = '>>> '
        self._hl_ps2 = self._ps2 = '... '
        self._output = None
        if color_scheme:
            color = get_color_for(Token.Generic.Prompt, color_scheme)
            self._hl_ps1 = ansiformat(color, self._ps1)
            self._hl_ps2 = ansiformat(color, self._ps2)
            self._lexer = Python3Lexer()
        else:
            self._lexer = LineLexer()

    def _colored(self, color, text):
        return ansiformat(color, text) if self._color_scheme else text

    def reset_interpreter(self):
        if self._use_ipython:
            import IPython
            from IPython.terminal.interactiveshell import \
                TerminalInteractiveShell

            class IPythonInterpreter(TerminalInteractiveShell,
                                     PresenterInterpreter):
                pass

            self._interpreter = IPythonInterpreter(confirm_exit=False)
            if not HAVE_HIGHLIGHTING or not self._color_scheme:
                self._interpreter.run_line_magic('colors', 'NoColor')

            interpreter = self._interpreter
            session_id = interpreter.history_manager.session_number
            history_queue = self._history_queue = queue.Queue()
            def monitor():
                if not self._interacting:
                    return
                it = interpreter.history_manager.get_range(session_id, -1)
                last_input = next(it, None)
                if last_input is not None:
                    history_queue.put(last_input[-1])

            if IPython.version_info < (2, 0):
                self._interpreter.register_post_execute(monitor)
            else:
                self._interpreter.events.register('post_run_cell', monitor)

            # Customize IPython to make it look like the CPYthon shell
            if IPython.version_info >= (5, 0):
                from IPython.terminal.prompts import ClassicPrompts
                self._interpreter.prompts = ClassicPrompts(self._interpreter)
            else:
                self._interpreter.prompt_manager.in_template = self._ps1
                self._interpreter.prompt_manager.in2_template = self._ps2
                self._interpreter.prompt_manager.out_template = ''
                self._interpreter.prompt_manager.justify = False
            self._interpreter.separate_in = ''
        else:
            ns = {'exit': Quitter(self, exit), 'quit': Quitter(self, quit)}
            if HAVE_HIGHLIGHTING and self._color_scheme:
                self._interpreter = HighlightingInterpreter(
                    color_scheme=self._color_scheme, locals=ns)
            else:
                self._interpreter = PresenterInterpreter(locals=ns)

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
             typing_delay=0, paginate=True):
        if self._output is not None:
            self._output.close()
            self._output = None
        ps1 = self._hl_ps1, len(self._ps1)
        ps2 = self._hl_ps2, len(self._ps2)
        hl_prompts = (ps1 if p == 'ps1' else ps2 for p in prompts)
        tokens = layout_code(self._lexer, statement, hl_prompts,
                             index, index_line)
        output = simulate_typing(tokens, self._color_scheme, typing_delay)
        if paginate:
            max_line = statement.count('\n') - 1
            for line_number, console_filled in output:
                if console_filled and line_number != max_line:
                    self._output = output
                    return True
        else:
            for _ in output:
                pass
        return False

    def show_more(self):
        for _, console_filled in self._output:
            if console_filled:
                return True
        return False

    def execute(self, statement, code=None):
        print(flush=True)
        if code is not None:
            self._interpreter.runcode(code)
        else:
            self._interpreter.compilesource(statement)
        print(end=self._hl_ps1, flush=True)

    def interact(self):
        print(end='\r')
        self._interacting = True
        if self._use_ipython:
            thread = Thread(target=self._interpreter.interact)
            thread.start()
            while thread.is_alive():
                try:
                    statement = self._history_queue.get(timeout=0.2)
                    yield statement.splitlines()
                except queue.Empty:
                    pass
        else:
            ps1 = self._colored('*green*', self._ps1)
            ps2 = self._colored('*green*', self._ps2)
            lines = []
            need_more = False
            print(end='\r', flush=True)
            while self._interacting:
                try:
                    try:
                        print(end=ps2 if need_more else ps1, flush=True)
                        line = input()
                        if PY2:
                            line = line.decode(sys.stdin.encoding)
                        lines.append(line)
                    except EOFError:
                        break
                    else:
                        source = '\n'.join(lines)
                        if PY2:
                            source = source.encode(sys.stdin.encoding)
                        need_more = self._interpreter.runsource(source)
                        if not need_more:
                            yield lines
                            lines = []
                except KeyboardInterrupt:
                    print(self._colored('*red*', '\nKeyboardInterrupt'),
                          flush=True)
                    lines = []
                    need_more = False
            print(flush=True)
        print(end=self._hl_ps1, flush=True)
        self._interacting = False

    def ask_where_to_go(self, max_index):
        new_index = ask_index(max_index, self._color_scheme)
        print(end=self._hl_ps1, flush=True)
        return new_index

    def help(self, commands_help):
        self.show('help()', ['ps1'], typing_delay=30)
        print()
        for command, keys, description in commands_help:
            hl_keys = ','.join('[' + self._colored('*yellow*', key) + ']'
                               for key in keys)
            print(' {}: {}\n   {}'.format(
                self._colored('*green*', command), hl_keys, description))
        print(end=self._hl_ps1, flush=True)

    def quit(self):
        self.show('quit()', ['ps1'], typing_delay=30)

    def end(self):
        print(flush=True)
