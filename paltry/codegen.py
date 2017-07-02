import ctypes as ct
import llvmlite.ir as ir

from paltry.datatypes import PtType, PtObject
import paltry.llvm_types as llvm_types


_type_map = {
    PtType.integer: llvm_types.PtContents_integer,
    PtType.double: llvm_types.PtContents_double,
    PtType.bytestring: llvm_types.PtContents_bytestring,
}



def _empty_object(bld, lib, local=False):
    if local:
        obj = bld.alloca(llvm_types.PtObject)
    else:
        obj = bld.call(
            lib['malloc'],
            (ir.Constant(lib['size_t'], ct.sizeof(PtObject)),)
        )
        return bld.bitcast(obj, llvm_types.PtObject.as_pointer())
    return obj


def _set_contents(bld, obj, type_, value):
    ptr = bld.gep(obj, (ir.Constant(ir.IntType(32), 0),
                        ir.Constant(ir.IntType(32), 0)))
    bld.store(ir.Constant(ir.IntType(32), int(type_)), ptr)

    ptr = bld.gep(obj, (ir.Constant(ir.IntType(32), 0),
                        ir.Constant(ir.IntType(32), 1)))
    ptr = bld.bitcast(ptr, _type_map[type_].as_pointer())
    bld.store(value, ptr)


def _codegen_integer(node, bld, mod, lib):
    obj = _empty_object(bld, lib)
    _set_contents(bld, obj, PtType.integer,
                  ir.Constant(llvm_types.PtContents_integer, node.contents.integer))
    return obj


def _codegen_double(node, bld, mod, lib):
    obj = _empty_object(bld, lib)
    _set_contents(bld, obj, PtType.double,
                  ir.Constant(llvm_types.PtContents_double, node.contents.double))
    return obj


def _codegen_bytestring(node, bld, mod, lib):
    type_ = ir.ArrayType(ir.IntType(8), len(node.contents.bytestring) + 1)
    buf = ir.GlobalVariable(mod, type_, name='##static')
    buf.global_constant = True
    buf.initializer = ir.Constant.literal_array([
        ir.Constant(ir.IntType(8), char)
        for char in node.contents.bytestring
    ] + [ir.Constant(ir.IntType(8), 0)])

    obj = _empty_object(bld, lib)
    _set_contents(bld, obj, PtType.bytestring,
                  bld.bitcast(buf, llvm_types.PtContents_bytestring))
    return obj


_node_dispatch = {
    PtType.integer: _codegen_integer,
    PtType.double: _codegen_double,
    PtType.bytestring: _codegen_bytestring,
}


def codegen(node, *args):
    return _node_dispatch[node.type](node, *args)
