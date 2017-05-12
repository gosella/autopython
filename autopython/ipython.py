# -*- coding: utf-8 -*-

from __future__ import print_function

from threading import Thread
from IPython.terminal.interactiveshell import TerminalInteractiveShell
from .compat import PY2, print, queue
from .highlighter import HAVE_HIGHLIGHTING, ansiformat
from .interactions import layout_code, simulate_typing, ask_index

if PY2:
    try:
        from IPython.lib.lexers import IPythonLexer
    except ImportError:
        from pygments.lexers import PythonLexer as IPythonLexer
else:
    try:
        from IPython.lib.lexers import IPython3Lexer as IPythonLexer
    except ImportError:
        from pygments.lexers import Python3Lexer as IPythonLexer


class Shell(TerminalInteractiveShell):
    INTERRUPT = object()
    END_SESSION = object()

    def __init__(self, input_queue, prompt_queue, user_queue, **kwargs):
        self.__input_queue = input_queue
        self.__prompt_queue = prompt_queue
        self.__user_queue = user_queue
        self.__interactive = True
        super(Shell, self).__init__(confirm_exit=False, **kwargs)
        # This prevents writing to the history db after every statement
        # (which delays a "Go to" command considerably).
        self.history_manager.db_cache_size = 10000

    def interact(self, interactive=True, display_banner=None):
        self.__interactive = interactive
        return super(Shell, self).interact(display_banner)

    def raw_input(self, prompt=''):
        in_prompt = self.separate_in + self.prompt_manager.render('in')
        self.separate_in = '\n'
        if self.__interactive:
            result = super(Shell, self).raw_input(prompt)
            self.__user_queue.put((result, in_prompt == prompt))
            return result

        print(end=prompt, flush=True)
        raw_prompt = 'in' if in_prompt == prompt else 'in2'
        prompt_len = len(self.prompt_manager.render(raw_prompt, color=False))
        self.__prompt_queue.put((prompt, prompt_len))
        result = self.__input_queue.get()
        if result is Shell.INTERRUPT:
            raise KeyboardInterrupt
        elif result is Shell.END_SESSION:
            self.ask_exit()
        else:
            return result


class PresenterShell(object):
    def __init__(self, color_scheme='default'):
        self._input_queue = queue.Queue()
        self._prompt_queue = queue.Queue()
        self._user_queue = queue.Queue()
        self._shell = None
        self._shell_thread = None
        self._color_scheme = color_scheme
        self._lexer = IPythonLexer()
        self._state = None

    def _create_shell(self):
        self._shell = Shell(self._input_queue, self._prompt_queue,
                            self._user_queue)
        if not HAVE_HIGHLIGHTING or not self._color_scheme:
            self._shell.run_line_magic('colors', 'NoColor')

    def _start_shell_thread(self, interactive, initial_separator):
        self._shell_thread = Thread(target=self._shell.interact,
                                    kwargs={'interactive': interactive})
        self._shell.separate_in = initial_separator
        self._shell_thread.start()

    def _stop_shell_thread(self):
        if self._shell_thread.is_alive():
            self._input_queue.put(Shell.END_SESSION)
            self._shell_thread.join()
            try:
                self._prompt_queue.get(timeout=0.02)
            except queue.Empty:
                pass

    def reset_interpreter(self):
        if self._shell_thread is not None:
            self._stop_shell_thread()
        self._create_shell()
        self._start_shell_thread(interactive=False, initial_separator='')

    def begin(self):
        self._create_shell()
        print('AutoI' + self._shell.banner, flush=True)
        self._start_shell_thread(interactive=False, initial_separator='')

    def control_c(self):
        self._cleanup_pagination()
        print(end='^C')
        self._input_queue.put(Shell.INTERRUPT)

    def _cleanup_pagination(self):
        if self._state is not None:
            self._state[0].close()
            self._state = None

    def show(self, statement, prompts, index=None, index_line=-1,
             typing_delay=0, paginate=True):
        def generate_prompts():
            while True:
                prompt, prompt_len = self._prompt_queue.get()
                yield '\r' + prompt.lstrip('\n'), prompt_len
        self._cleanup_pagination()
        lines = statement.splitlines()
        last_line_number = len(lines) - 1
        tokens = layout_code(self._lexer, statement, generate_prompts(),
                             index, index_line)
        output = simulate_typing(tokens, self._color_scheme, typing_delay)
        if paginate:
            for line_number, console_filled in output:
                if console_filled and line_number != last_line_number:
                    self._state = (output, lines, last_line_number)
                    return True
                if line_number < last_line_number:
                    self._input_queue.put(lines[line_number])
        else:
            for line_number, _ in output:
                if line_number < last_line_number:
                    self._input_queue.put(lines[line_number])
        return False

    def show_more(self):
        output, lines, last_line_number = self._state
        for line_number, console_filled in output:
            if console_filled:
                return True
            if line_number < last_line_number:
                self._input_queue.put(lines[line_number])
        return False

    def execute(self, statement, code=None):
        print(flush=True)
        self._input_queue.put(statement.splitlines()[-1])

    def interact(self):
        self._stop_shell_thread()
        self._start_shell_thread(interactive=True, initial_separator='\r')
        lines = []
        while self._shell_thread.is_alive():
            try:
                line, is_first_line = self._user_queue.get(timeout=0.2)
                if is_first_line and lines:
                    yield lines
                    lines = []
                lines.append(line)
            except queue.Empty:
                pass
        if lines:
            yield lines
        self._start_shell_thread(interactive=False, initial_separator='\n')

    def ask_where_to_go(self, max_index):
        while self._prompt_queue.qsize() == 0:
            pass
        new_index = ask_index(max_index, self._color_scheme)
        if new_index is None:
            print(end=self._shell.prompt_manager.render('in'), flush=True)
        return new_index

    def _fake_show(self, statement, prompts, typing_delay=0):
        def generate_prompts():
            renderer = self._shell.prompt_manager.render
            for prompt in prompts:
                kind = 'in' if prompt == 'ps1' else 'in2'
                yield renderer(kind), len(renderer(kind, color=False))
        while self._prompt_queue.qsize() == 0:
            pass
        tokens = layout_code(self._lexer, statement, generate_prompts())
        for _ in simulate_typing(tokens, self._color_scheme, typing_delay):
            pass

    def help(self, commands_help):
        def colored(color, text):
            return ansiformat(color, text) if self._color_scheme else text
        self._fake_show('help()', ['ps1'], typing_delay=30)
        print(colored('*teal*', '\n\nAvailable actions:\n'))
        for command, keys, description in commands_help:
            hl_keys = ','.join('[' + colored('*yellow*', key) + ']'
                               for key in keys)
            print('  {}: {}\n    {}\n'.format(
                colored('*green*', command), hl_keys, description))
        print(end=self._shell.prompt_manager.render('in'), flush=True)

    def quit(self):
        self.show('quit()', ['ps1'], typing_delay=30)

    def end(self):
        self._stop_shell_thread()
        print('\n', flush=True)
