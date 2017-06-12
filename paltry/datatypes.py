import codecs
import ctypes as ct
import enum
from itertools import tee


class PtType(enum.IntEnum):
    """Enumerates the fundamental data types in Paltry. Corresponds to the
    PtContents union.
    """
    integer = enum.auto()
    double = enum.auto()
    symbol = enum.auto()
    bytestring = enum.auto()
    cons = enum.auto()
    function = enum.auto()

# Since many of the fields of these types are self-referential, we set the
# fields after declaring the classes.

class PtCons(ct.Structure):
    """A PtCons is a pair with two pointers to PtObjects: the car and the cdr."""
    pass

class PtContents(ct.Union):
    """A union covering all the possible fundamental data types. Corresponds to the
    PtType enum.
    """

    def __init__(self, **kwargs):
        super(PtContents, self).__init__()
        if kwargs:
            key, value = next(iter(kwargs.items()))
            assert key in {'integer', 'double', 'symbol', 'bytestring', 'cons', 'function'}
            setattr(self, key, value)


class PtSymbol(ct.Structure):
    """A symbol is a pair of a name and a binding."""

    def __init__(self, name, ident, binding=None):
        buffer = name.encode('utf-8')
        if isinstance(binding, PtObject):
            binding = ct.pointer(binding)
        super(PtSymbol, self).__init__(ct.c_char_p(buffer), ident, binding)
        self.buffer = buffer


class PtObject(ct.Structure):
    """The primary structure representing a lisp object. It has a type field (see
    the PtType enum) and a contents field (see the PtContents union).
    """

    # Table of interned symbols
    __intern = {}
    __symbol_id = 0

    def __init__(self, *args):
        """Create a lisp object from one of the fundamental data types (integers,
        floats or strings).

        Also functions as the underlying constructor for one of the more
        specialized constructors.
        """
        if len(args) == 2 and isinstance(args[0], PtType) and isinstance(args[1], PtContents):
            super(PtObject, self).__init__(*args)
            return

        value, = args
        if isinstance(value, int):
            super(PtObject, self).__init__(PtType.integer, PtContents(integer=value))
        elif isinstance(value, float):
            super(PtObject, self).__init__(PtType.double, PtContents(double=value))
        elif isinstance(value, str):
            self.buffer = value.encode('utf-8')
            super(PtObject, self).__init__(
                PtType.bytestring,
                PtContents(bytestring=ct.c_char_p(self.buffer)),
            )
        else:
            raise TypeError('Invalid type to PtObject: {}'.format(type(value)))

    @staticmethod
    def symbol(name):
        """Creates an uninterned symbol with the given name."""
        obj = PtObject(PtType.symbol, PtContents(symbol=PtSymbol(name, PtObject.__symbol_id)))
        PtObject.__symbol_id += 1
        return obj

    @staticmethod
    def intern(name):
        """Finds or creates the interned symbol with the given name."""
        try:
            return PtObject.__intern[name]
        except KeyError:
            symbol = PtObject.symbol(name)
            PtObject.__intern[name] = symbol
            return symbol

    @staticmethod
    def cons(car, cdr):
        """Creates a cons cell from two objects."""
        assert isinstance(car, PtObject)
        assert isinstance(cdr, PtObject)

        obj = PtObject(
            PtType.cons,
            PtContents(cons=PtCons(ct.pointer(car), ct.pointer(cdr))),
        )
        obj.buffer = (car, cdr)
        return obj

    @staticmethod
    def list(elements):
        """Creates a list (a tree of cons cells) from a list of elements."""
        elements = list(elements)
        assert all(isinstance(element, PtObject) for element in elements)

        ret = PtObject.nil
        for element in elements[::-1]:
            ret = PtObject.cons(element, ret)
        return ret

    @staticmethod
    def initialize():
        """Initializes the interned symbol table."""

        # nil
        nil = PtObject(PtType.cons, PtContents(cons=PtCons(None, None)))

        # t
        t = PtObject.symbol('t')
        t.contents.symbol.binding = ct.pointer(t)

        PtObject.__intern.update({
            'nil': nil,
            't': t,
        })

        PtObject.nil = nil

    def __bool__(self):
        """All PtObjects except nil are truthy."""
        if self.type != PtType.cons:
            return True
        if self.contents.cons.car or self.contents.cons.cdr:
            return True
        return False

    @property
    def car(self):
        """Accesses the car of a cons cell."""
        assert self.type == PtType.cons
        assert bool(self)
        return self.contents.cons.car.contents

    @property
    def cdr(self):
        """Accesses the cdr of a cons cell."""
        assert self.type == PtType.cons
        assert bool(self)
        return self.contents.cons.cdr.contents

    def __str__(self):
        if self.type == PtType.integer:
            return str(self.contents.integer)
        elif self.type == PtType.double:
            return str(self.contents.double)
        elif self.type == PtType.symbol:
            return self.contents.symbol.name.decode('utf-8')
        elif self.type == PtType.bytestring:
            s = codecs.escape_encode(self.contents.bytestring)[0].decode('utf-8')
            return '"{}"'.format(s.replace('"', '\\"'))
        elif self.type == PtType.cons:
            if not self.contents.cons.car or not self.contents.cons.cdr:
                return 'nil'
            car, cdr = self.car, self.cdr
            ret = '{}'.format(car)
            while True:
                if not bool(cdr):
                    break
                if cdr.type != PtType.cons:
                    ret += ' . {}'.format(cdr)
                    break
                car, cdr = cdr.car, cdr.cdr
                ret += ' {}'.format(car)
            return '({})'.format(ret)

    __repr__ = __str__

    def __eq__(self, other):
        """Strict type-based equality."""
        assert isinstance(other, PtObject)
        if self.type != other.type:
            return False
        if self.type == PtType.integer:
            return self.contents.integer == other.contents.integer
        elif self.type == PtType.double:
            return self.contents.double == other.contents.double
        elif self.type == PtType.bytestring:
            return self.contents.bytestring == other.contents.bytestring
        elif self.type == PtType.function:
            return self.contents.function == other.contents.function
        elif self.type == PtType.symbol:
            return self.contents.symbol.ident == other.contents.symbol.ident
        elif self.type == PtType.cons:
            if not bool(self) and not bool(other):
                return True
            return self.car == other.car and self.cdr == other.cdr


# Initialize the structure fields
PtCons._fields_ = [
    ('car', ct.POINTER(PtObject)),
    ('cdr', ct.POINTER(PtObject)),
]
PtSymbol._fields_ = [
    ('name', ct.c_char_p),
    ('ident', ct.c_int64),
    ('binding', ct.POINTER(PtObject)),
]
PtContents._fields_ = [
    ('integer', ct.c_longlong),
    ('double', ct.c_double),
    ('bytestring', ct.c_char_p),
    ('symbol', PtSymbol),
    ('cons', PtCons),
    ('function', ct.c_void_p),
]
PtObject._fields_ = [
    ('type', ct.c_int32),
    ('contents', PtContents),
]

# Initialize the internal symbol table
PtObject.initialize()
