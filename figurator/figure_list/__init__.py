from __future__ import print_function
from .. import process_includes, load_spec

def create_latex_figure_list(defs, captions=None, collect_dir=None):
    # Generates a list of figures and descriptions that can
    # be piped to pandoc and/or latex
    spec = load_spec(defs, captions=captions)
    __ = process_includes(spec,
        collect_dir=collect_dir,
        starred_floats=False)

    for cfg, (id,item) in zip(spec,__):
        print(item)
