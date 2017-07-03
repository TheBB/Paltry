from contextlib import contextmanager
import ctypes as ct
import llvmlite.ir as ir
import llvmlite.binding as llvm

from paltry.datatypes import PtObject, PtFunction
import paltry.llvm_types as llvm_types


llvm.initialize()
llvm.initialize_native_target()
llvm.initialize_native_asmprinter()

_size_t = ir.IntType(8 * ct.sizeof(ct.c_size_t))
_ptr = ir.IntType(8).as_pointer()


class PaltryVM:

    def __init__(self):
        target = llvm.Target.from_default_triple()
        target_machine = target.create_target_machine()
        self.engine = llvm.create_mcjit_compiler(llvm.parse_assembly(''), target_machine)

    @contextmanager
    def module(self, name, show_ir=False):
        module = ir.Module(name)

        stdlib = {
            'size_t': _size_t,
            'malloc': ir.Function(module, ir.FunctionType(_ptr, (_size_t,)), name='malloc')
        }

        func = ir.Function(module, llvm_types.PtFunction, '##{}##init'.format(name))
        block = func.append_basic_block('entry')
        bld = ir.IRBuilder(block)

        yield bld, module, stdlib

        if show_ir:
            print(str(module))

        refmod = llvm.parse_assembly(str(module))
        refmod.verify()
        self.engine.add_module(refmod)
        self.engine.finalize_object()

    def run_init(self, name):
        addr = self.engine.get_function_address('##{}##init'.format(name))
        func = PtFunction(addr)
        value = func(0, None)
        if value:
            value = ct.cast(value, ct.POINTER(PtObject))
            return value.contents
