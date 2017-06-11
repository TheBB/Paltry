import codecs

from paltry.gen_grammar import PaltrySemantics as GenSemantics, PaltryParser
from paltry.datatypes import PtObject


class PaltrySemantics(GenSemantics):

    def symbol(self, name):
        return PtObject.symbol(name)

    def string(self, value):
        value = codecs.escape_decode(bytes(value[1:-1], 'utf-8'))[0].decode('utf-8')
        return PtObject(value)

    def bin_integer(self, value):
        return PtObject(int(value[2:], 2))

    def oct_integer(self, value):
        return PtObject(int(value[2:], 8))

    def hex_integer(self, value):
        return PtObject(int(value[2:], 16))

    def dec_integer(self, value):
        return PtObject(int(value))

    def double(self, value):
        return PtObject(float(value))

    def sexp(self, elements):
        return PtObject.list(elements)

    def quot(self, value):
        return PtObject.list([PtObject.symbol('quote'), value])

    def bquot(self, value):
        return PtObject.list([PtObject.symbol('backquote'), value])
