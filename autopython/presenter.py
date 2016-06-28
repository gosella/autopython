# -*- coding: utf-8 -*-

from __future__ import print_function

import os.path

from datetime import datetime
from . import console, parser


def lower_upper_key(char):
    return char.lower(), char.upper()


class Presenter(object):
    KEY_PREV = (console.PGUP,) + lower_upper_key('p')
    KEY_NEXT = (console.PGDN, ' ', '\n', '\r')
    KEY_AGAIN = lower_upper_key('r')
    KEY_GOTO = lower_upper_key('g')
    KEY_SHELL = lower_upper_key('s')
    KEY_EXIT = lower_upper_key('q')

    BEFORE_TYPING, BEFORE_EXECUTING, BEFORE_QUITING, QUITING = range(4)

    def __init__(self, shell, typing_delay=30, logging=False):
        self._shell = shell
        self._typing_delay = typing_delay
        self._logging = logging
        self._logger = None
        self._script_loaded = False

    def load_file(self, filename):
        self._statements = parser.parse_file(filename)
        self._script_name = filename
        self._script_loaded = True

    def run(self):
        if not self._script_loaded:
            raise ValueError('Presentation script not loaded')

        self._begin()
        try:
            while self._state != Presenter.QUITING:
                try:
                    key = console.getch()
                except KeyboardInterrupt:
                    continue
                if key in Presenter.KEY_NEXT:
                    self._next()
                elif key in Presenter.KEY_PREV:
                    self._prev()
                elif key in Presenter.KEY_AGAIN:
                    self._again()
                elif key in Presenter.KEY_GOTO:
                    self._go_to()
                elif key in Presenter.KEY_SHELL:
                    self._interact()
                elif key in Presenter.KEY_EXIT:
                    self._quit()
        finally:
            self._end()

    def _begin(self):
        self._index = 0
        self._state = Presenter.BEFORE_TYPING
        self._shell.begin()
        self._start_logging()

    def _end(self):
        self._shell.end()
        pending = len(self._statements) - self._index
        if pending > 0:
            reason = 'Quiting with {} more statement{} to show.'.format(
                     pending, 's' if pending > 1 else '')
        else:
            reason = 'The End.'
        self._log(reason)
        self._end_logging()

    def _next(self):
        if self._state == Presenter.BEFORE_TYPING:
            if self._index < len(self._statements):
                info = self._statements[self._index]
                index = self._index + 1
                lines = info.statement.splitlines()[info.first_line:]
                self._log('Showing statement {} (on line {}):'.format(index,
                          info.line_number),
                          *(' ' + line for line in lines if line.strip()))
                self._shell.show(info.statement, info.prompts,
                                 index, info.first_line, self._typing_delay)
                self._state = Presenter.BEFORE_EXECUTING
            else:
                self._quit()
        elif self._state == Presenter.BEFORE_EXECUTING:
            info = self._statements[self._index]
            self._index += 1
            motive = 'Failing on' if info.code is None else 'Executing'
            self._log('{} statement {} (on line {}).'.format(motive,
                      self._index, info.line_number))
            self._shell.execute(info.statement, info.code)
            self._state = Presenter.BEFORE_TYPING
        elif self._state == Presenter.BEFORE_QUITING:
            self._state = Presenter.QUITING

    def _prev(self):
        if self._state in (Presenter.BEFORE_TYPING,
                           Presenter.BEFORE_EXECUTING):
            if self._index > 0:
                if self._state == Presenter.BEFORE_EXECUTING:
                    self._shell.control_c()
                    self._state = Presenter.BEFORE_TYPING
                self._index -= 1
                self._next()
        elif self._state == Presenter.BEFORE_QUITING:
            self._shell.control_c()
            self._state = Presenter.BEFORE_TYPING
            if self._index == len(self._statements):
                self._index -= 1
            if self._index > 0:
                self._next()

    def _again(self):
        if self._state == Presenter.BEFORE_TYPING:
            if self._index > 0:
                self._index -= 1
                self._next()
        elif self._state == Presenter.BEFORE_EXECUTING:
            self._next()

    def _go_to(self):
        if not self._statements:
            return
        if self._state in (Presenter.BEFORE_EXECUTING,
                           Presenter.BEFORE_QUITING):
            self._shell.control_c()
            self._state = Presenter.BEFORE_TYPING

        new_index = self._shell.ask_where_to_go(len(self._statements))
        if new_index is None:
            return
        self._log('Continuing on statement {} (line {}).'.format(
                  new_index + 1, self._statements[new_index].line_number))
        if new_index < self._index:
            self._shell.reset_interpreter()
            self._index = 0
        if new_index > 0:
            try:
                original_typing_delay = self._typing_delay
                self._typing_delay = 0
                original_logging = self._logging
                self._logging = False
                while self._index < new_index:
                    self._next()
            finally:
                self._typing_delay = original_typing_delay
                self._logging = original_logging
        self._next()

    def _interact(self):
        if self._state in (Presenter.BEFORE_EXECUTING,
                           Presenter.BEFORE_QUITING):
            self._shell.control_c()
            self._state = Presenter.BEFORE_TYPING
        if self._state == Presenter.BEFORE_TYPING:
            self._log('Entering interactive mode.')
            for statement in self._shell.interact():
                lines = [' ' + line for line in statement if line.strip()]
                if lines:
                    self._log('Executing:', *lines)
            self._log('Leaving interactive mode.')

    def _quit(self):
        if self._state in (Presenter.BEFORE_QUITING, Presenter.QUITING):
            self._state = Presenter.QUITING
        else:
            if self._state == Presenter.BEFORE_EXECUTING:
                self._shell.control_c()
            self._shell.quit()
            self._state = Presenter.BEFORE_QUITING

    def _start_logging(self):
        if self._logging:
            if self._logger is not None:
                self._logger.close()
            start_time = datetime.now().strftime('%Y-%m-%d')
            base_name = os.path.splitext(self._script_name)[0]
            log_name = '{}-{}.log'.format(base_name, start_time)
            self._logger = open(log_name, 'at')
            init_msg = '=====  AutoPython initiated  ====='
            separator = '=' * len(init_msg)
            self._log(separator, init_msg, separator)

    def _end_logging(self):
        if self._logging and self._logger is not None:
            self._logger.close()
            self._logger = None

    def _log(self, message, *rest):
        if self._logging:
            timestamp = datetime.now().strftime('[%Y-%m-%d %H:%M:%S]')
            print(timestamp, message, file=self._logger)
            indent = ' ' * len(timestamp)
            for line in rest:
                print(indent, line.rstrip(), file=self._logger)
