from __future__ import print_function
from os import path
import re
import pypandoc


def inline_figure_filter(spec, includes):
    pattern = re.compile("<!--\[\[(.+)\]\]-->")

    items = {l:d for l,d in includes}
    def fn(matchobj):
        try:
            id = matchobj.group(1)
            return items[id]
        except KeyError:
            # Don't replace if we can't find include
            return matchobj.group(0)
    def match_function(text):
        return pattern.sub(fn,text)
    return match_function

def latex_figure_list(spec, includes, **kwargs):
    """
    Generates a list of figures and descriptions that can
    be piped to pandoc and/or latex
    """
    for cfg, (id,item) in zip(spec,includes):
        print(item)

typedef = {
    'Figure': 'fig:',
    'Table': 'tab:'
}

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
    pattern = re.compile("`(\[|\()?((Figure|Table)s?\s+)([\w\s,]+)(\]|\))?`")
    def fn(m):
        s = m.group(1) or ""
        s += m.group(2)
        body = m.group(4)
        s += replace_body(body, type=m.group(3))
        s += m.group(5) or "" # Close parens if any
        return s

    return pattern.sub(fn,text)
