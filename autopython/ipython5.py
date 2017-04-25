# -*- coding: utf-8 -*-

from __future__ import print_function

from IPython.terminal.interactiveshell import TerminalInteractiveShell
from prompt_toolkit.key_binding.input_processor import InputProcessor, KeyPress
from prompt_toolkit.keys import Keys
from prompt_toolkit.token import Token
from threading import Thread, Lock, Event

from . import console
from .compat import PY2, print, queue

import random
import signal
import time

if PY2:
    from IPython.lib.lexers import IPythonLexer
else:
    from IPython.lib.lexers import IPython3Lexer as IPythonLexer


class PresenterShell(object):
    def __init__(self, color_scheme='default'):
        self._shell = None
        self._interacting = False
        self._prompt_ready = Event()
        self._shell_thread = None
        self._color_scheme = color_scheme
        self._lexer = IPythonLexer()

        # We simulate the user typing monkey-patching the `feed` method 
        # of the prompt_toolkit InputProcessor, filtering keystrokes according
        # to whether the user is presenting or in interactive mode.

        self._input_lock = Lock()

        self._real_feed = InputProcessor.feed
        def new_feed(processor, key_press):
            with self._input_lock:
                if self._interacting or key_press.key == Keys.CPRResponse:
                    self._real_feed(processor, key_press)
        InputProcessor.feed = new_feed

        self._real_process_keys = InputProcessor.process_keys
        def new_process_keys(processor):
            with self._input_lock:
                self._real_process_keys(processor)
        InputProcessor.process_keys = new_process_keys


    def _create_shell(self):
        self._shell = shell = TerminalInteractiveShell(confirm_exit=False)
        self._pt_cli = pt_cli = shell.pt_cli

        # We go into the guts of IPython's prompt and replace the provider of
        # the default rprompt tokens to show the current sentence index.
        self._index = None
        def get_rprompt_tokens(cli):
            if self._index is None:
                return []
            return [(Token.Generic.Strong, ' (%d)' % self._index)]

        rprompt = pt_cli.application.layout.children[0].floats[-1]
        rprompt.content.content.get_tokens = get_rprompt_tokens
        rprompt.top = 0

        # We need to know when the next prompt is ready, so we use an Event.
        def new_prompt(sender):
            assert not self._prompt_ready.is_set()
            self._prompt_ready.set()

        pt_cli.on_start += new_prompt

        # After each successful input, we hide the rprompt and log the
        # last executed sentence (if we are in interactive mode).
        self._history_queue = history_queue = queue.Queue()
        
        def input_done(sender):
            self._index = None
            if self._interacting:
                return_value = sender.return_value()
                if return_value is not None:
                    history_queue.put(return_value.text)

        pt_cli.on_stop += input_done

    def _start_shell_thread(self):
        self._shell_thread = Thread(target=self._shell.interact)
        self._shell_thread.start()

    def _stop_shell_thread(self):
        if self._shell_thread.is_alive():
            self._shell.ask_exit()
            self._pt_cli.exit()
            self._pt_cli.input_processor.process_keys()
            self._shell_thread.join()
            self._wait_prompt()

    def _wait_prompt(self):
        self._prompt_ready.wait()
        self._prompt_ready.clear()

    def reset_interpreter(self):
        if self._shell_thread is not None:
            self._stop_shell_thread()
        self._create_shell()
        self._start_shell_thread()

    def begin(self):
        self._create_shell()
        print(end='AutoI' + self._shell.banner, flush=True)
        self._start_shell_thread()

    def control_c(self):
        self._index = None

        input_processor = self._pt_cli.input_processor
        feed = self._real_feed
        feed(input_processor, KeyPress(Keys.ControlC))
        input_processor.process_keys()

        # self._pt_cli.abort()

        # self._pt_cli.reset(reset_current_buffer=True)
        # self._pt_cli.renderer.request_absolute_cursor_position()
        # self._pt_cli.invalidate()

        self._prompt_ready.set()

    def _simulate_typing(self, statement, index, index_line, typing_delay):
        input_processor = self._pt_cli.input_processor
        feed = self._real_feed
        process_keys = self._real_process_keys
        delay = typing_delay / 1000.0
        lines = statement.splitlines()
        last_line = len(lines) - 1
        prev_sigint_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)
        try:
            console.disable_echo()
            self._wait_prompt()

            for line, text in enumerate(lines):
                # if not text and line < index_line:
                #     with self._input_lock:
                #         feed(input_processor, KeyPress(Keys.Escape))
                #         feed(input_processor, KeyPress(Keys.Enter))
                #         process_keys(input_processor)
                #     self._wait_prompt()
                #     continue

                # if line == index_line:
                #     self._index = index
                #     self._pt_cli.invalidate()

                for char in text:
                    with self._input_lock:
                        feed(input_processor, KeyPress(char))
                        process_keys(input_processor)
                    if delay and not char.isspace():
                        time.sleep(delay * (0.5 + random.random()))

                if line != last_line:
                    with self._input_lock:
                        feed(input_processor, KeyPress('\n'))
                        process_keys(input_processor)
        finally:
            signal.signal(signal.SIGINT, prev_sigint_handler)
            console.enable_echo()

    def show(self, statement, prompts, index=None, index_line=-1,
             typing_delay=0):
        self._simulate_typing(statement, index, index_line, typing_delay)

    def execute(self, statement, code=None):
        input_processor = self._pt_cli.input_processor
        feed = self._real_feed
        with self._input_lock:
            feed(input_processor, KeyPress(Keys.Escape))
            feed(input_processor, KeyPress(Keys.Enter))
            self._real_process_keys(input_processor)

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
        for _ in simulate_typing(statement, generate_prompts(),
                                 color_scheme=self._color_scheme,
                                 typing_delay=typing_delay,
                                 lexer=self._lexer):
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
