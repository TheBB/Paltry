from paltry.parser import PaltryParser, PaltrySemantics


def test_parsing():
    parser = PaltryParser(semantics=PaltrySemantics())
    parse = lambda s: parser.parse(s, 'exp')

    assert str(parse('quux')) == 'quux'
    assert str(parse('"alpha"')) == '"alpha"'
    assert str(parse('120')) == '120'
    assert str(parse('120.0e1')) == '1200.0'
    assert str(parse('0xf')) == '15'
    assert str(parse('0o7')) == '7'
    assert str(parse('0b1')) == '1'
    assert str(parse('(a b c d "e")')) == '(a b c d "e")'
    assert str(parse("'quoted")) == '(quote quoted)'
    assert str(parse("'(a list goes here)")) == '(quote (a list goes here))'
    assert str(parse("`(a list goes here)")) == '(backquote (a list goes here))'
