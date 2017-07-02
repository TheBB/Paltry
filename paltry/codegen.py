import llvmlite.ir as ir

from paltry.datatypes import PtType
import paltry.llvm_types as llvm_types


def codegen(node, builder):
    if node.type == PtType.integer:
        obj = builder.alloca(llvm_types.PtObject)

        ptr = builder.gep(obj, (ir.Constant(ir.IntType(32), 0),
                                ir.Constant(ir.IntType(32), 0)))
        builder.store(ir.Constant(ir.IntType(32), int(PtType.integer)), ptr)

        ptr = builder.gep(obj, (ir.Constant(ir.IntType(32), 0),
                                ir.Constant(ir.IntType(32), 1)))
        ptr = builder.bitcast(ptr, llvm_types.PtContents_integer.as_pointer())
        builder.store(ir.Constant(llvm_types.PtContents_integer, node.contents.integer), ptr)

        return builder.load(obj)

    pass
