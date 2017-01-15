from __future__ import print_function
from os import path
import re
import pypandoc
from .interface import load_spec
from .processors import process_includes

pattern = re.compile("<!--\[\[(.+)\]\]-->")

def inline_figure_filter(spec, **kwargs):
    includes = process_includes(spec, **kwargs)

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

def latex_figure_list(ctx, spec, **kwargs):
    """
    Generates a list of figures and descriptions that can
    be piped to pandoc and/or latex
    """
    __ = process_includes(spec, **kwargs)
    for cfg, (id,item) in zip(spec,__):
        print(item)
