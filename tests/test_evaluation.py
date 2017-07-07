from paltry.datatypes import PtObject
from paltry.codegen import codegen
from paltry import PaltryVM
from paltry.parser import PaltryParser, PaltrySemantics


_vm = PaltryVM()
_parser = PaltryParser(semantics=PaltrySemantics())

def check_result(code, value):
    ast = _parser.parse(code, 'toplevel')
    assert _vm.eval_code(ast) == value


def test_literals():
    check_result('0', PtObject(0))
    check_result('-1', PtObject(-1))
    check_result('0xf', PtObject(15))

    check_result('2.1', PtObject(2.1))
    check_result('-0.0', PtObject(0.0))

    check_result('""', PtObject(''))
    check_result('"alpha"', PtObject('alpha'))


def test_quote():
    check_result("'symbol", PtObject.intern('symbol'))
    check_result("''symbol", PtObject.list([
        PtObject.intern('quote'), PtObject.intern('symbol')
    ]))
    check_result("'(a b c)", PtObject.list([
        PtObject.intern(s) for s in ['a', 'b', 'c']
    ]))
    check_result("'(a . b)", PtObject.cons(
        PtObject.intern('a'), PtObject.intern('b')
    ))
    check_result(
        "'(a b . c)",
        PtObject.cons(
            PtObject.intern('a'),
            PtObject.cons(
                PtObject.intern('b'),
                PtObject.intern('c'))))


def test_let():
    check_result('(let ())', PtObject.nil)
    check_result('(let () 1)', PtObject(1))
    check_result('(let (a) a)', PtObject.nil)
    check_result('(let ((a)) a)', PtObject.nil)
    check_result('(let ((a nil)) a)', PtObject.nil)
    check_result('(let ((a 3)) a)', PtObject(3))
    check_result('(let ((a 1)) (let ((b a)) b))', PtObject(1))


def test_begin():
    check_result('(begin)', PtObject.nil)
    check_result('(begin 1)', PtObject(1))
    check_result('(begin 1 2 3)', PtObject(3))


def test_if():
    check_result('(if t 1)', PtObject(1))
    check_result('(if nil 1)', PtObject.nil)
    check_result('(if nil 1 2)', PtObject(2))
    check_result('(if nil 1 2 3)', PtObject(3))


def test_runtime():
    check_result('(intern "alpha")', PtObject.intern('alpha'))
