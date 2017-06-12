from paltry.datatypes import PtObject
from paltry.parser import PaltryParser, PaltrySemantics


def test_parsing():
    parser = PaltryParser(semantics=PaltrySemantics())
    parse = lambda s: parser.parse(s, 'exp')

    assert parse('quux') == PtObject.intern('quux')
    assert parse('"alpha"') == PtObject('alpha')
    assert parse('120') == PtObject(120)
    assert parse('120.0e1') == PtObject(1200.0)
    assert parse('0xf') == PtObject(15)
    assert parse('0o7') == PtObject(7)
    assert parse('0b1') == PtObject(1)
    assert parse('(a b c d "e")') == PtObject.list([
        PtObject.intern('a'), PtObject.intern('b'), PtObject.intern('c'),
        PtObject.intern('d'), PtObject('e'),
    ])
    assert parse("'quoted") == PtObject.list([
        PtObject.intern('quote'), PtObject.intern('quoted')
    ])
    assert parse("'(a list goes here)") == PtObject.list([
        PtObject.intern('quote'),
        PtObject.list([
            PtObject.intern('a'), PtObject.intern('list'),
            PtObject.intern('goes'), PtObject.intern('here'),
        ]),
    ])
    assert parse("`(a list goes here)")  == PtObject.list([
        PtObject.intern('backquote'),
        PtObject.list([
            PtObject.intern('a'), PtObject.intern('list'),
            PtObject.intern('goes'), PtObject.intern('here'),
        ]),
    ])
