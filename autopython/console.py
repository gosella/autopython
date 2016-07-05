# -*- coding: utf-8 -*-

# Mostly refactored from:
# URL: https://bitbucket.org/techtonik/python-pager
# Author:  anatoly techtonik <techtonik@gmail.com>
# License: Public Domain (use MIT if the former doesn't work for you)

import os
import sys

# Dealing with the terminal in different OSs
if os.name == 'nt':
    # Windows constants
    # http://msdn.microsoft.com/en-us/library/ms683231%28v=VS.85%29.aspx
    STD_INPUT_HANDLE = -10
    STD_OUTPUT_HANDLE = -11
    STD_ERROR_HANDLE = -12

    # get console handle
    from ctypes import windll, Structure, byref
    try:
        from ctypes.wintypes import SHORT, WORD, DWORD
    except ImportError:
        from ctypes import c_short as SHORT, c_ushort as WORD, c_ulong as DWORD
    console_handle = windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)

    # CONSOLE_SCREEN_BUFFER_INFO Structure
    class COORD(Structure):
        _fields_ = [("X", SHORT), ("Y", SHORT)]

    class SMALL_RECT(Structure):
        _fields_ = [("Left", SHORT), ("Top", SHORT),
                    ("Right", SHORT), ("Bottom", SHORT)]

    class CONSOLE_SCREEN_BUFFER_INFO(Structure):
        _fields_ = [("dwSize", COORD),
                    ("dwCursorPosition", COORD),
                    ("wAttributes", WORD),
                    ("srWindow", SMALL_RECT),
                    ("dwMaximumWindowSize", DWORD)]

    def _get_window_size():
        """Return (width, height) of available window area on Windows.
           (0, 0) if no console is allocated.
        """
        sbi = CONSOLE_SCREEN_BUFFER_INFO()
        ret = windll.kernel32.GetConsoleScreenBufferInfo(console_handle, byref(sbi))
        if ret == 0:
            return 0, 0
        return (sbi.srWindow.Right - sbi.srWindow.Left + 1,
                sbi.srWindow.Bottom - sbi.srWindow.Top + 1)

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
    import array
    import fcntl
    import termios
    import tty

    def _get_window_size():
        """Return (width, height) of console terminal on POSIX system.
           (0, 0) on IOError, i.e. when no console is allocated.
        """
        # see README.txt for reference information
        # http://www.kernel.org/doc/man-pages/online/pages/man4/tty_ioctl.4.html

        """
        struct winsize {
            unsigned short ws_row;
            unsigned short ws_col;
            unsigned short ws_xpixel;   /* unused */
            unsigned short ws_ypixel;   /* unused */
        };
        """
        winsize = array.array("H", [0] * 4)
        try:
            fcntl.ioctl(sys.stdout.fileno(), termios.TIOCGWINSZ, winsize)
        except IOError:
            # for example IOError: [Errno 25] Inappropriate ioctl for device
            # when output is redirected
            # [ ] TODO: check fd with os.isatty
            pass
        return winsize[1], winsize[0]

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


def get_width():
    """
    Return width of available window in characters.  If detection fails,
    return value of standard width 80.  Coordinate of the last character
    on a line is -1 from returned value.

    Windows part uses console API through ctypes module.
    *nix part uses termios ioctl TIOCGWINSZ call.
    """
    return _get_window_size()[0] or 80


def get_height():
    """
    Return available window height in characters or 25 if detection fails.
    Coordinate of the last line is -1 from returned value.

    Windows part uses console API through ctypes module.
    *nix part uses termios ioctl TIOCGWINSZ call.
    """
    return _get_window_size()[1] or 25


def getch():
    """
    Wait for keypress, return character or a list of characters.

    Arrows and special keys generate a sequence of characters, so if there are
    extra symbols in input buffer, this function returns list.
    """
    return _getch()
