from __future__ import print_function
from os import path
import re

def inline_figure_filter(spec, includes):
    pattern = re.compile("\\\inlinefigure\{(fig|tbl):(.+)\}")

    items = {l:d for l,d in includes}
    def fn(matchobj):
        try:
            id = matchobj.group(2)
            return items[id]
        except KeyError:
            # Replace with empty string if we can't find include
            return ""
    def match_function(text):
        return pattern.sub(fn,text)
    return match_function

def latex_figure_list(spec, includes, outfile, **kwargs):
    """
    Generates a list of figures and descriptions that can
    be piped to pandoc and/or latex
    """
    # Enable subsetting of, e.g. figures and tables...
    type = kwargs.pop("type",'figure')
    for cfg, (id,item) in zip(spec,includes):
        if type != cfg.get('type','figure'):
            continue
        print(item, file=outfile)

typedef = {
    'Figure': 'fig:',
    'Table': 'tbl:'
}

__ref_pattern = re.compile("`(\[|\()?((Figure|Table)s?\s+)([\w\s,]+)(\]|\))?`")
__body_pattern = re.compile("(\w+)(\{(\w+)\})?(,?\s*)")
ignored_words = ['and','of','or','to']
def replace_body(text, type='Figure'):
    d = typedef[type]
    def fn(m):
        word = m.group(1)
        if word in ignored_words:
            s = word
        else:
            s = "\\ref{"+d+word+"}"
        s += m.group(3) or "" # material afterwards
        s += m.group(4) or "" # comma and trailing space
        return s
    return __body_pattern.sub(fn,text)

def figure_id_filter(text):
    """
    Matches figure and table definition schemes, converting
    to the appropriate references: e.g.
    `Figure gupta` -> Figure \ref{fig:gupta}
    `Figure gupta{c}` -> Figure \ref{fig:gupta}c
    `[Tables ranjeev and stuff]` -> [Figures \ref{tab:ranjeev} and \ref{tab:stuff}]
    """
    def fn(m):
        s = m.group(1) or ""
        s += m.group(2)
        body = m.group(4)
        s += replace_body(body, type=m.group(3))
        s += m.group(5) or "" # Close parens if any
        return s

    return __ref_pattern.sub(fn,text)

