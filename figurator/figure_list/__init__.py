from __future__ import print_function
from os import path
from .. import process_includes, load_spec

__dirname = path.dirname(__file__)
templates = path.join(__dirname,"templates")

def create_latex_figure_list(defs,
        captions=None, collect_dir=None,
        citation_backend=None):
    # Generates a list of figures and descriptions that can
    # be piped to pandoc and/or latex
    spec = load_spec(defs, captions=captions)
    __ = process_includes(spec,
        collect_dir=collect_dir,
        template_dir=templates,
        citation_backend=citation_backend,
        starred_floats=False)

    for cfg, (id,item) in zip(spec,__):
        print(item)
