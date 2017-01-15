from __future__ import print_function
import codecs
from os import path
from click import pass_context
from .captions import integrate_captions
from .interface import load_spec
from .collect import update_filenames

def write_file(fn, text):
    with codecs.open(fn,"w",encoding="utf8") as f:
        f.write(text)

def update_defaults(item, **kwargs):
    """
    Updates passed configuration for figures and
    tables with default values
    """
    __ = dict(
        scale=None,
        type='figure',
        two_column=False,
        width='20pc',
        sideways=False,
        starred_floats=True,
        caption="")

    __.update(**item)

    __["env"] = __["type"]

    if __['two_column']:
        __['width'] = '42pc'
    # Add stars to two_column floats
    # `True` by default
    # (this is useful for two-column layouts)
    if kwargs.pop("starred_floats",True):
        if __["two_column"]:
            __["env"] += "*"

    return __

### Process includes ###
@pass_context
def process_includes(ctx, spec, **kwargs):
    """
    If invoked with `collect_dir` kwarg, we modify filenames to
    point to collected file. If not, filename points to original
    location
    """
    # Load spec if we haven't already
    spec = load_spec(spec,
        captions=kwargs.pop('captions', None))
    # We modify filenames if invoked with `collect_dir`
    collect_dir = kwargs.pop('collect_dir',None)
    if collect_dir is not None:
        spec = update_filenames(spec, collect_dir)

    for item in spec:
        cfg = update_defaults(item, **kwargs)
        # Process caption
        if cfg['caption'] != "":
            cfg['caption'] = ctx.pandoc_processor(cfg["caption"])

        method = getattr(ctx.tex_renderer,"make_"+cfg['type'])
        yield cfg["id"], method(cfg)

