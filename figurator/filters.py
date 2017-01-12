"""
Miscellaneous filters for latex renderer
"""
from pandas import isnull

def nominal(value,rounding=2):
    if isnull(value):
        return '--'
    fs = "{0:."+str(rounding)+"f}"
    try:
        return fs.format(value.n)
    except AttributeError:
        return fs.format(value)

def uncertain(value,rounding=2):
    fs = "{0:."+str(rounding)+"f}"
    d = tuple(fs.format(i)\
        for i in (value.n, value.s))
    try:
        return "$\pm$".join(d)
    except AttributeError:
        return value
