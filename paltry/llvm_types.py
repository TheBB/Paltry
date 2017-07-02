import ctypes as ct
import llvmlite.ir as ir

import paltry.datatypes as datatypes


_ptr = ir.IntType(8).as_pointer()


PtContents = ir.IntType(8 * ct.sizeof(datatypes.PtContents))

PtObject = ir.LiteralStructType((
    ir.IntType(32),             # type
    PtContents,                 # contents
))

PtCons = ir.LiteralStructType((
    PtObject.as_pointer(),      # car
    PtObject.as_pointer(),      # cdr
))

PtSymbol = ir.LiteralStructType((
    _ptr,                       # name
    ir.IntType(64),             # ident
    PtObject.as_pointer(),      # binding
))

PtContents_integer = ir.IntType(8 * ct.sizeof(ct.c_longlong))
PtContents_double = ir.DoubleType()
PtContents_bytestring = _ptr
PtContents_function = _ptr

PtFunction = ir.FunctionType(
    PtObject.as_pointer(), (),
)
