from __future__ import print_function
from os import path
import re
from . import process_includes, load_spec
from .util import apply_defaults

__dirname = path.dirname(__file__)
templates = path.join(__dirname,"templates")
pattern = re.compile("<!--\[\[(.+)\]\]-->")

def inline_figure_filter(defs, **kwargs):
    captions=kwargs.pop('captions',None)
    spec = load_spec(defs, captions=captions)
    kwargs['template_dir'] = templates
    includes = process_includes(spec, **apply_defaults(kwargs))

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

