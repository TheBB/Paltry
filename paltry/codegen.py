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


def _obj_ptr(bld, obj, indirection=1):
    location = ct.addressof(obj)
    type_ = llvm_types.PtObject
    for _ in range(indirection):
        type_ = type_.as_pointer()
    return bld.inttoptr(ir.Constant(ir.IntType(64), location), type_)


def _codegen_integer(node, bld, mod, lib, ns):
    obj = _empty_object(bld, lib)
    _set_contents(
        bld, obj, PtType.integer,
        ir.Constant(llvm_types.PtContents_integer, node.contents.integer)
    )
    return obj


def _codegen_double(node, bld, mod, lib, ns):
    obj = _empty_object(bld, lib)
    _set_contents(
        bld, obj, PtType.double,
        ir.Constant(llvm_types.PtContents_double, node.contents.double)
    )
    return obj


def _codegen_bytestring(node, bld, mod, lib, ns):
    type_ = ir.ArrayType(ir.IntType(8), len(node.contents.bytestring) + 1)
    buf = ir.GlobalVariable(mod, type_, name='##static')
    buf.initializer = ir.Constant.literal_array([
        ir.Constant(ir.IntType(8), char)
        for char in node.contents.bytestring
    ] + [ir.Constant(ir.IntType(8), 0)])

    obj = _empty_object(bld, lib)
    _set_contents(
        bld, obj, PtType.bytestring,
        bld.bitcast(buf, llvm_types.PtContents_bytestring)
    )
    return obj


def _return_if_zero(bld, value):
    zerop = bld.icmp_signed('==', bld.ptrtoint(value, ir.IntType(64)), ir.Constant(ir.IntType(64), 0))
    with bld.if_then(zerop, likely=False):
        bld.ret(bld.inttoptr(
            ir.Constant(ir.IntType(64), 0),
            llvm_types.PtObject.as_pointer(),
        ))


def _codegen_symbol(node, bld, mod, lib, ns):
    symbol = node.contents.symbol
    if symbol in ns:
        return ns[symbol]

    value = bld.load(_obj_ptr(bld, symbol.binding, indirection=2))
    _return_if_zero(bld, value)
    return value


def _codegen_cons(node, bld, mod, lib, ns):
    if node == PtObject.nil:
        return _obj_ptr(bld, PtObject.nil)


_node_dispatch = {
    PtType.integer: _codegen_integer,
    PtType.double: _codegen_double,
    PtType.bytestring: _codegen_bytestring,
    PtType.symbol: _codegen_symbol,
    PtType.cons: _codegen_cons,
}

def codegen(node, *args):
    return _node_dispatch[node.type](node, *args)
