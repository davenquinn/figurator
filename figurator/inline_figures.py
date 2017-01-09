from __future__ import print_function
from os import path
import re
from . import process_includes, load_spec

__dirname = path.dirname(__file__)
templates = path.join(__dirname,"templates")
pattern = re.compile("<!--\[\[(.+)\]\]-->")

def inline_figure_filter(defs, captions=None, collect_dir=None, template_dir=None):

    spec = load_spec(defs, captions=captions)
    includes = process_includes(spec,
        collect_dir=collect_dir,
        # We should load from list
        # of paths instead of single dirctory
        template_dir=template_dir or templates)

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

