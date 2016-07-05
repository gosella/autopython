# -*- coding: utf-8 -*-

import os
import sys

try:
    from shutil import get_terminal_size
except ImportError:
    from backports.shutil_get_terminal_size import get_terminal_size

# Dealing with the terminal in different OSs
if os.name == 'nt':
    import msvcrt

    def _getch():
        a = msvcrt.getwch()
        if a == u'\x00' or a == u'\xe0':
            b = msvcrt.getwch()
            return [a, b]
        return a

    def enable_echo():
        pass

    def disable_echo():
        pass

    ESC = u'\x1b'
    ENTER = u'\x0d'
    LEFT = [u'\xe0', u'K']
    UP = [u'\xe0', u'H']
    RIGHT = [u'\xe0', u'M']
    DOWN = [u'\xe0', u'P']
    PGUP = [u'\xe0', u'I']
    PGDN = [u'\xe0', u'Q']

elif os.name == 'posix':
    # Mostly refactored from:
    # URL: https://bitbucket.org/techtonik/python-pager
    # Author:  anatoly techtonik <techtonik@gmail.com>
    # License: Public Domain (use MIT if the former doesn't work for you)

    import termios
    import tty

    def _getch():
        fd = sys.stdin.fileno()

        # save old terminal settings, because we are changing them
        old_settings = termios.tcgetattr(fd)
        try:
            # set terminal to "cbreak" mode, in which driver returns
            # one char at a time instead of one line at a time
            #
            # tty.setcbreak() is just a helper for tcsetattr() call, see
            # http://hg.python.org/cpython/file/c6880edaf6f3/Lib/tty.py
            tty.setcbreak(fd)
            ch = sys.stdin.read(1)

            # clear input buffer placing all available chars into morech
            newattr = termios.tcgetattr(fd)   # change terminal settings
            #  to allow non-blocking read
            newattr[6][termios.VMIN] = 0      # CC structure
            newattr[6][termios.VTIME] = 0
            termios.tcsetattr(fd, termios.TCSANOW, newattr)

            morech = []
            while True:
                ch2 = sys.stdin.read(1)
                if ch2 == '':
                    break
                morech.append(ch2)
        finally:
            # restore terminal settings. Do this when all output is
            # finished - TCSADRAIN flag
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

        if morech:
            morech.insert(0, ch)
            ch = morech

        return ch

    def enable_echo():
        fd = sys.stdin.fileno()
        attrs = termios.tcgetattr(fd)
        attrs[3] = attrs[3] | termios.ECHO
        termios.tcsetattr(fd, termios.TCSADRAIN, attrs)

    def disable_echo():
        fd = sys.stdin.fileno()
        attrs = termios.tcgetattr(fd)
        attrs[3] = attrs[3] & ~termios.ECHO
        termios.tcsetattr(fd, termios.TCSADRAIN, attrs)

    ESC = '\x1b'
    ENTER = '\n'
    LEFT = [ESC, '[', 'D']
    UP = [ESC, '[', 'A']
    RIGHT = [ESC, '[', 'C']
    DOWN = [ESC, '[', 'B']
    PGUP = [ESC, '[', '5', '~']
    PGDN = [ESC, '[', '6', '~']

else:
    # 'mac', 'os2', 'ce', 'java' need implementations
    raise ImportError("platform not supported")


def getch():
    """
    Wait for keypress, return character or a list of characters.

    Arrows and special keys generate a sequence of characters, so if there are
    extra symbols in input buffer, this function returns list.
    """
    return _getch()


__all__ = ['get_terminal_size', 'enable_echo', 'disable_echo', 'getch']
