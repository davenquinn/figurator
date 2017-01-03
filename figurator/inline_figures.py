from __future__ import print_function
from os import path
import re
from . import process_includes, load_spec

__dirname = path.dirname(__file__)
templates = path.join(__dirname,"templates")
pattern = re.compile("<!--\[\[(.+)\]\]-->")

def inline_figure_filter(defs, captions=None, collect_dir=None):
    spec = load_spec(defs, captions=captions)
    includes = process_includes(spec,
        collect_dir=collect_dir,
        template_dir=templates)

    items = {l:d for l,d in includes}
    def fn(matchobj):
        try:
            return items[matchobj.group(1)]
        except KeyError:
            # Don't replace if we can't find include
            return matchobj.group(0)
    def match_function(text):
        return pattern.sub(fn,text)
    return match_function

