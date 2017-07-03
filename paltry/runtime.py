import ctypes as ct

from paltry.datatypes import PtObject


@PtObject.callback('display')
def function(*args):
    print(' '.join(str(arg) for arg in args))
    return PtObject.nil
