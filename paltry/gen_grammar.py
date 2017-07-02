#!/usr/bin/env python
# -*- coding: utf-8 -*-

# CAVEAT UTILITOR
#
# This file was automatically generated by TatSu.
#
#    https://pypi.python.org/pypi/tatsu/
#
# Any changes you make to it will be overwritten the next time
# the file is generated.


from __future__ import print_function, division, absolute_import, unicode_literals

from tatsu.buffering import Buffer
from tatsu.parsing import Parser
from tatsu.parsing import tatsumasu
from tatsu.util import re, generic_main  # noqa


KEYWORDS = {}  # type: ignore


class PaltryBuffer(Buffer):
    def __init__(
        self,
        text,
        whitespace=None,
        nameguard=None,
        comments_re=None,
        eol_comments_re=';.*?$',
        ignorecase=None,
        namechars='',
        **kwargs
    ):
        super(PaltryBuffer, self).__init__(
            text,
            whitespace=whitespace,
            nameguard=nameguard,
            comments_re=comments_re,
            eol_comments_re=eol_comments_re,
            ignorecase=ignorecase,
            namechars=namechars,
            **kwargs
        )


class PaltryParser(Parser):
    def __init__(
        self,
        whitespace=None,
        nameguard=None,
        comments_re=None,
        eol_comments_re=';.*?$',
        ignorecase=None,
        left_recursion=True,
        parseinfo=True,
        keywords=None,
        namechars='',
        buffer_class=PaltryBuffer,
        **kwargs
    ):
        if keywords is None:
            keywords = KEYWORDS
        super(PaltryParser, self).__init__(
            whitespace=whitespace,
            nameguard=nameguard,
            comments_re=comments_re,
            eol_comments_re=eol_comments_re,
            ignorecase=ignorecase,
            left_recursion=left_recursion,
            parseinfo=parseinfo,
            keywords=keywords,
            namechars=namechars,
            buffer_class=buffer_class,
            **kwargs
        )

    @tatsumasu()
    def _toplevel_(self):  # noqa

        def block0():
            self._exp_()
        self._closure(block0)

    @tatsumasu()
    def _exp_(self):  # noqa
        with self._choice():
            with self._option():
                self._literal_()
            with self._option():
                self._sexp_()
            with self._option():
                self._quot_()
            with self._option():
                self._bquot_()
            with self._option():
                self._unquot_splice_()
            with self._option():
                self._unquot_()
            self._error('no available options')

    @tatsumasu()
    def _literal_(self):  # noqa
        with self._choice():
            with self._option():
                self._double_()
            with self._option():
                self._integer_()
            with self._option():
                self._symbol_()
            with self._option():
                self._string_()
            self._error('no available options')

    @tatsumasu()
    def _symbol_(self):  # noqa
        self._pattern(r'([^\\\"\\\'`,\n\t\(\) ])+')

    @tatsumasu()
    def _string_(self):  # noqa
        self._pattern(r'\"(\\.|[^\"])+\"')

    @tatsumasu()
    def _integer_(self):  # noqa
        with self._choice():
            with self._option():
                self._bin_integer_()
            with self._option():
                self._oct_integer_()
            with self._option():
                self._hex_integer_()
            with self._option():
                self._dec_integer_()
            self._error('no available options')

    @tatsumasu()
    def _bin_integer_(self):  # noqa
        self._pattern(r'0b[0-1]+')

    @tatsumasu()
    def _oct_integer_(self):  # noqa
        self._pattern(r'0o[0-7]+')

    @tatsumasu()
    def _dec_integer_(self):  # noqa
        self._pattern(r'[0-9]+')

    @tatsumasu()
    def _hex_integer_(self):  # noqa
        self._pattern(r'0x[0-9a-f]+')

    @tatsumasu()
    def _double_(self):  # noqa
        self._pattern(r'[0-9]*([0-9]\.|\.[0-9])[0-9]*([eE][+-]?[0-9]+)?')

    @tatsumasu()
    def _sexp_(self):  # noqa
        self._token('(')

        def block1():
            self._exp_()
        self._closure(block1)
        self.name_last_node('@')
        self._token(')')

    @tatsumasu()
    def _quot_(self):  # noqa
        self._token("'")
        self._exp_()
        self.name_last_node('@')

    @tatsumasu()
    def _bquot_(self):  # noqa
        self._token('`')
        self._exp_()
        self.name_last_node('@')

    @tatsumasu()
    def _unquot_(self):  # noqa
        self._token(',')
        self._exp_()
        self.name_last_node('@')

    @tatsumasu()
    def _unquot_splice_(self):  # noqa
        self._token(',@')
        self._exp_()
        self.name_last_node('@')


class PaltrySemantics(object):
    def toplevel(self, ast):  # noqa
        return ast

    def exp(self, ast):  # noqa
        return ast

    def literal(self, ast):  # noqa
        return ast

    def symbol(self, ast):  # noqa
        return ast

    def string(self, ast):  # noqa
        return ast

    def integer(self, ast):  # noqa
        return ast

    def bin_integer(self, ast):  # noqa
        return ast

    def oct_integer(self, ast):  # noqa
        return ast

    def dec_integer(self, ast):  # noqa
        return ast

    def hex_integer(self, ast):  # noqa
        return ast

    def double(self, ast):  # noqa
        return ast

    def sexp(self, ast):  # noqa
        return ast

    def quot(self, ast):  # noqa
        return ast

    def bquot(self, ast):  # noqa
        return ast

    def unquot(self, ast):  # noqa
        return ast

    def unquot_splice(self, ast):  # noqa
        return ast


def main(filename, startrule, **kwargs):
    with open(filename) as f:
        text = f.read()
    parser = PaltryParser()
    return parser.parse(text, startrule, filename=filename, **kwargs)


if __name__ == '__main__':
    import json
    from tatsu.util import asjson

    ast = generic_main(main, PaltryParser, name='Paltry')
    print('AST:')
    print(ast)
    print()
    print('JSON:')
    print(json.dumps(asjson(ast), indent=2))
    print()
