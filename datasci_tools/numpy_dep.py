from numpy import *
from numpy import array as _arr

def array(*args,**kwargs):
    try:
        x = _arr(*args,**kwargs)
    except:
        kwargs["dtype"] = "object"
        x = _arr(*args,**kwargs)
    return x


import numpy
def max(*args,**kwargs):
    return numpy.max(*args,**kwargs)

def min(*args,**kwargs):
    return numpy.min(*args,**kwargs)

def round(*args,**kwargs):
    return numpy.round(*args,**kwargs)

def abs(*args,**kwargs):
    return numpy.abs(*args,**kwargs)

bool = numpy.bool_
float = numpy.float64
# def bool(*args,**kwargs):
#     return numpy.bool_(*args,**kwargs)

# from numpy import int as _int
# def int(*args,**kwargs):
#     return _int(*args,**kwargs)
