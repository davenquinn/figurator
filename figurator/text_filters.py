from __future__ import print_function
from os import path
import re
import pypandoc

pattern = re.compile("<!--\[\[(.+)\]\]-->")

def inline_figure_filter(spec, includes):

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
