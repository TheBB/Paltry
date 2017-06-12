from paltry.datatypes import PtObject


def test_integer():
    obj = PtObject(3)
    assert str(obj) == '3'
    assert obj == PtObject(3)
    assert obj != PtObject(4)


def test_float():
    obj = PtObject(3.0)
    assert str(obj) == '3.0'
    assert obj == PtObject(3.0)
    assert obj != PtObject(-3.0)


def test_string():
    obj = PtObject('abc')
    assert str(obj) == '"abc"'
    assert obj == PtObject('abc')
    assert obj != PtObject('abcc')


def test_symbol():
    obj = PtObject.symbol('abc')
    assert str(obj) == 'abc'
    assert obj != PtObject.symbol('abc')

    obj = PtObject.intern('abc')
    assert obj != PtObject.symbol('abc')
    assert obj == PtObject.intern('abc')
    assert obj is PtObject.intern('abc')


def test_cons():
    assert str(PtObject.nil) == 'nil'
    assert PtObject.nil == PtObject.nil

    obj = PtObject.cons(PtObject.intern('def'), PtObject.intern('ghi'))
    assert str(obj) == '(def . ghi)'
    assert obj == PtObject.cons(PtObject.intern('def'), PtObject.intern('ghi'))
    assert obj != PtObject.cons(PtObject.symbol('def'), PtObject.intern('ghi'))
    assert obj != PtObject.cons(PtObject.intern('def'), PtObject.symbol('ghi'))

    obj = PtObject.cons(
        PtObject.intern('a'),
        PtObject.cons(
            PtObject.intern('b'),
            PtObject.cons(
                PtObject.intern('c'),
                PtObject.intern('d'))))
    assert str(obj) == '(a b c . d)'
    assert obj == PtObject.cons(
        PtObject.intern('a'),
        PtObject.cons(
            PtObject.intern('b'),
            PtObject.cons(
                PtObject.intern('c'),
                PtObject.intern('d'))))

    obj = PtObject.cons(
        PtObject.intern('a'),
        PtObject.cons(
            PtObject.intern('b'),
            PtObject.cons(
                PtObject.intern('c'),
                PtObject.nil)))
    assert str(obj) == '(a b c)'
    assert obj == PtObject.cons(
        PtObject.intern('a'),
        PtObject.cons(
            PtObject.intern('b'),
            PtObject.cons(
                PtObject.intern('c'),
                PtObject.nil)))

    obj = PtObject.list([
        PtObject.intern('a'),
        PtObject.intern('b'),
        PtObject.intern('c'),
        PtObject.intern('d'),
        PtObject.intern('e'),
    ])
    assert str(obj) == '(a b c d e)'
    assert obj == PtObject.list([
        PtObject.intern('a'),
        PtObject.intern('b'),
        PtObject.intern('c'),
        PtObject.intern('d'),
        PtObject.intern('e'),
    ])
