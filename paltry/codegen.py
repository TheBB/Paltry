import ctypes as ct
import llvmlite.ir as ir

from paltry.datatypes import PtType
import paltry.llvm_types as llvm_types


_type_map = {
    PtType.integer: llvm_types.PtContents_integer,
    PtType.double: llvm_types.PtContents_double,
    PtType.bytestring: llvm_types.PtContents_bytestring,
}



def _empty_object(builder):
    obj = builder.alloca(llvm_types.PtObject)
    return obj


def _set_contents(builder, obj, type_, value):
    ptr = builder.gep(obj, (ir.Constant(ir.IntType(32), 0),
                            ir.Constant(ir.IntType(32), 0)))
    builder.store(ir.Constant(ir.IntType(32), int(type_)), ptr)

    ptr = builder.gep(obj, (ir.Constant(ir.IntType(32), 0),
                            ir.Constant(ir.IntType(32), 1)))
    ptr = builder.bitcast(ptr, _type_map[type_].as_pointer())
    builder.store(value, ptr)


def _codegen_integer(node, module, builder):
    obj = _empty_object(builder)
    _set_contents(builder, obj, PtType.integer,
                  ir.Constant(llvm_types.PtContents_integer, node.contents.integer))
    return builder.load(obj)


def _codegen_double(node, module, builder):
    obj = _empty_object(builder)
    _set_contents(builder, obj, PtType.double,
                  ir.Constant(llvm_types.PtContents_double, node.contents.double))
    return builder.load(obj)


def _codegen_bytestring(node, module, builder):
    type_ = ir.ArrayType(ir.IntType(8), len(node.contents.bytestring) + 1)
    buf = ir.GlobalVariable(module, type_, name='##static')
    buf.global_constant = True
    buf.initializer = ir.Constant.literal_array([
        ir.Constant(ir.IntType(8), char)
        for char in node.contents.bytestring
    ] + [ir.Constant(ir.IntType(8), 0)])

    obj = _empty_object(builder)
    _set_contents(builder, obj, PtType.bytestring,
                  builder.bitcast(buf, llvm_types.PtContents_bytestring))

    return builder.load(obj)


_node_dispatch = {
    PtType.integer: _codegen_integer,
    PtType.double: _codegen_double,
    PtType.bytestring: _codegen_bytestring,
}


def codegen(node, module, builder):
    return _node_dispatch[node.type](node, module, builder)
