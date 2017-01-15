from __future__ import print_function
from os import path
from .. import process_includes, load_spec
from ..util import apply_defaults

__dirname = path.dirname(__file__)
templates = path.join(__dirname,"templates")

def create_latex_figure_list(defs, **kwargs):
    captions=kwargs.pop('captions',None)

    # Generates a list of figures and descriptions that can
    # be piped to pandoc and/or latex
    spec = load_spec(defs, captions=captions)
    __ = process_includes(spec,**apply_defaults(kwargs, template_dir=templates))

    for cfg, (id,item) in zip(spec,__):
        print(item)
