# -*- coding: utf-8 -*-

try:
    import colorama
    import pygments

    colorama.init()
    HAVE_HIGHLIGHTING = True

    del colorama
    del pygments
except ImportError:
    HAVE_HIGHLIGHTING = False


class LineLexer(object):
    def __init__(self, *args, **kwargs):
        pass

    def get_tokens_unprocessed(self, text):
        prev_pos = 0
        while True:
            pos = text.find('\n', prev_pos)
            if pos == -1:
                break
            yield prev_pos, Token.Text, text[prev_pos:pos]
            yield pos, Token, '\n'
            prev_pos = pos + 1

        if prev_pos < len(text):
            yield prev_pos, Token.Text, text[prev_pos:]


if HAVE_HIGHLIGHTING:
    from pygments import highlight
    from pygments.console import ansiformat
    from pygments.formatters import TerminalFormatter
    from pygments.lexers import Python3Lexer
    from pygments.lexers import Python3TracebackLexer as TracebackLexer
    from pygments.token import Token

    COLOR_SCHEMES = {
        'default': {
            Token:                        '',
            Token.Index:                  '**',
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
            Token.Prompt:                 'darkgreen',
            Token.PromptNum:              'green',
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
    }

    def get_color_for(ttype, color_scheme='default'):
        scheme = COLOR_SCHEMES.get(color_scheme)
        if scheme is None:
            return ''
        while ttype:
            color = scheme.get(ttype)
            if color:
                return color
            ttype = ttype[:-1]
        return ''

else:
    class Token:
        pass

    Token.Index = object()
    Token.Prompt = object()
    Token.Text = object()
    Token.Generic = Token

    COLOR_SCHEMES = {'default': {}}

    Python3Lexer = LineLexer
    TracebackLexer = LineLexer

    class TerminalFormatter(object):
        def __init__(self, *args, **kwargs):
            pass

    def highlight(code, lexer, formatter, outfile=None):
        if outfile is None:
            return code
        outfile.write(code)

    def ansiformat(attr, text):
        return text

    def get_color_for(ttype, color_scheme='default'):
        return None
