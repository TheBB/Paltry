import ctypes as ct
from functools import partial
import llvmlite.ir as ir

from paltry.datatypes import PtType, PtObject
import paltry.llvm_types as llvm_types


_type_map = {
    PtType.integer: llvm_types.PtContents_integer,
    PtType.double: llvm_types.PtContents_double,
    PtType.bytestring: llvm_types.PtContents_bytestring,
    PtType.cons: llvm_types.PtCons,
}

_i8 = ir.IntType(8)
_i32 = ir.IntType(32)
_i64 = ir.IntType(64)
_i8c = partial(ir.Constant, _i8)
_i32c = partial(ir.Constant, _i32)
_i64c = partial(ir.Constant, _i64)


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
    ptr = bld.gep(obj, (_i32c(0), _i32c(0)))
    bld.store(ir.Constant(_i32, int(type_)), ptr)
    ptr = bld.gep(obj, (_i32c(0), _i32c(1)))
    ptr = bld.bitcast(ptr, _type_map[type_].as_pointer())
    bld.store(value, ptr)


def _obj_ptr(bld, obj, indirection=1):
    location = ct.addressof(obj)
    type_ = llvm_types.PtObject
    for _ in range(indirection):
        type_ = type_.as_pointer()
    return bld.inttoptr(_i64c(location), type_)


def _return_if_zero(bld, value):
    zerop = bld.icmp_signed('==', bld.ptrtoint(value, _i64), ir.Constant(_i64, 0))
    with bld.if_then(zerop, likely=False):
        bld.ret(bld.inttoptr(_i64c(0), llvm_types.PtObject.as_pointer()))


def _return_if_not_type(bld, value, type_):
    ptr = bld.gep(value, (_i32c(0), _i32c(0)))
    value_type = bld.load(ptr)
    zerop = bld.icmp_signed('!=', value_type, _i32c(int(type_)))
    with bld.if_then(zerop, likely=False):
        bld.ret(bld.inttoptr(_i64c(0), llvm_types.PtObject.as_pointer()))


def _is_truthy(bld, value):
    zerop = bld.icmp_signed(
        '!=', bld.ptrtoint(value, _i64), ir.Constant(_i64, ct.addressof(PtObject.nil))
    )
    return zerop


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
    type_ = ir.ArrayType(_i8, len(node.contents.bytestring) + 1)
    buf = ir.GlobalVariable(mod, type_, name='##static')
    buf.initializer = ir.Constant.literal_array(
        [_i8c(char) for char in node.contents.bytestring] + [_i8c(0)]
    )

    obj = _empty_object(bld, lib)
    _set_contents(
        bld, obj, PtType.bytestring,
        bld.bitcast(buf, llvm_types.PtContents_bytestring)
    )
    return obj


def _codegen_symbol(node, bld, mod, lib, ns):
    symbol = node.contents.symbol
    if symbol in ns:
        return ns[symbol]

    value = bld.load(_obj_ptr(bld, symbol.binding, indirection=2))
    _return_if_zero(bld, value)
    return value


def _codegen_cons(node, bld, mod, lib, ns):
    if not bool(node):
        return _obj_ptr(bld, PtObject.nil)
    head, tail = node.car, node.cdr
    if head == PtObject.intern('quote'):
        return codegen_copy(tail.car, bld, mod, lib, ns)
    if head == PtObject.intern('begin'):
        nodes = list(tail) or [PtObject.nil]
        for node in nodes:
            retval = codegen(node, bld, mod, lib, ns)
        return retval
    if head == PtObject.intern('if'):
        true_branch = PtObject.nil
        false_branch = []
        cond, tail = tail.car, tail.cdr
        if tail:
            true_branch, false_branch = tail.car, list(tail.cdr)
        false_branch = false_branch or [PtObject.nil]
        cond = codegen(cond, bld, mod, lib, ns)
        with bld.if_else(_is_truthy(bld, cond)) as (true, false):
            with true:
                true_val = codegen(true_branch, bld, mod, lib, ns)
                true_blk = bld.block
            with false:
                for node in false_branch:
                    false_val = codegen(node, bld, mod, lib, ns)
                false_blk = bld.block
        retval = bld.phi(llvm_types.PtObject.as_pointer())
        retval.add_incoming(true_val, true_blk)
        retval.add_incoming(false_val, false_blk)
        return retval
    if head == PtObject.intern('let'):
        bindings, body = tail.car, tail.cdr
        sub_ns = dict(ns)
        for binding in bindings:
            value = PtObject.nil
            if binding.type == PtType.symbol:
                name = binding
            else:
                name = binding.car
                if binding.cdr:
                    value = binding.cdr.car
            sub_ns[name.contents.symbol] = codegen(value, bld, mod, lib, ns)
        retval = None
        for expr in body:
            retval = codegen(expr, bld, mod, lib, sub_ns)
        if retval is None:
            return codegen(PtObject.nil, bld, mod, lib, ns)
        return retval
    function = codegen(head, bld, mod, lib, ns)
    _return_if_not_type(bld, function, PtType.function)

    args = list(tail)
    arglist_type = ir.ArrayType(llvm_types.PtObject.as_pointer(), len(args))
    arglist = bld.alloca(arglist_type)
    for i, arg in enumerate(args):
        value = codegen(arg, bld, mod, lib, ns)
        ptr = bld.gep(arglist, (_i32c(0), _i32c(i)))
        bld.store(value, ptr)

    func_ptr_loc = bld.gep(function, (_i32c(0), _i32c(1)))
    func_ptr_loc = bld.bitcast(func_ptr_loc, llvm_types.PtFunction.as_pointer().as_pointer())
    func_ptr = bld.load(func_ptr_loc)
    args_ptr = bld.gep(arglist, (_i32c(0), _i32c(0)))
    retval = bld.call(func_ptr, (_i32c(len(args)), args_ptr))
    _return_if_zero(bld, retval)

    return retval


def _codegen_copy_symbol(node, bld, *args):
    return _obj_ptr(bld, node)


def _codegen_copy_cons(node, bld, mod, lib, ns):
    if not bool(node):
        return _obj_ptr(bld, PtObject.nil)

    car = codegen_copy(node.car, bld, mod, lib, ns)
    cdr = codegen_copy(node.cdr, bld, mod, lib, ns)

    cons = bld.alloca(llvm_types.PtCons)
    ptr = bld.gep(cons, (_i32c(0), _i32c(0)))
    bld.store(car, ptr)
    ptr = bld.gep(cons, (_i32c(0), _i32c(1)))
    bld.store(cdr, ptr)

    obj = _empty_object(bld, lib)
    _set_contents(bld, obj, PtType.cons, bld.load(cons))
    return obj


_node_dispatch = {
    PtType.integer: _codegen_integer,
    PtType.double: _codegen_double,
    PtType.bytestring: _codegen_bytestring,
    PtType.symbol: _codegen_symbol,
    PtType.cons: _codegen_cons,
}

def codegen(node, *args):
    return _node_dispatch[node.type](node, *args)


_node_copy_dispatch = {
    PtType.integer: _codegen_integer,
    PtType.double: _codegen_double,
    PtType.bytestring: _codegen_bytestring,
    PtType.symbol: _codegen_copy_symbol,
    PtType.cons: _codegen_copy_cons,
}

def codegen_copy(node, *args):
    return _node_copy_dispatch[node.type](node, *args)
