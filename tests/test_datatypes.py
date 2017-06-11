from paltry.datatypes import PtObject


def test_integer():
    obj = PtObject(3)
    assert str(obj) == '3'


def test_float():
    obj = PtObject(3.0)
    assert str(obj) == '3.0'


def test_string():
    obj = PtObject('abc')
    assert str(obj) == '"abc"'


def test_symbol():
    obj = PtObject.symbol('abc')
    assert str(obj) == 'abc'


def test_cons():
    assert str(PtObject.nil) == 'nil'

    obj = PtObject.cons(PtObject.symbol('def'), PtObject.symbol('ghi'))
    assert str(obj) == '(def . ghi)'

    obj = PtObject.cons(
        PtObject.symbol('a'),
        PtObject.cons(
            PtObject.symbol('b'),
            PtObject.cons(
                PtObject.symbol('c'),
                PtObject.symbol('d'))))
    assert str(obj) == '(a b c . d)'

    obj = PtObject.cons(
        PtObject.symbol('a'),
        PtObject.cons(
            PtObject.symbol('b'),
            PtObject.cons(
                PtObject.symbol('c'),
                PtObject.nil)))
    assert str(obj) == '(a b c)'

    obj = PtObject.list([
        PtObject.symbol('a'),
        PtObject.symbol('b'),
        PtObject.symbol('c'),
        PtObject.symbol('d'),
        PtObject.symbol('e'),
    ])
    assert str(obj) == '(a b c d e)'
