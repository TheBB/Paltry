import ctypes as ct

from paltry.datatypes import PtObject


@PtObject.callback()
def display(*args):
    print(' '.join(str(arg) for arg in args))
    return PtObject.nil


@PtObject.callback()
def intern(name):
    return PtObject.intern(name.string)
