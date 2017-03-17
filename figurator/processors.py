from __future__ import print_function
import codecs
import yaml
from os import path
from click import pass_context
from .captions import integrate_captions
from .text_filters import figure_id_filter
from .includes import reorder_includes

def collected_filename(cfg, collect_dir):
    """
    Update filenames to point to files
    collected by the figure-collection
    function
    """
    ext = path.splitext(cfg['file'])[1]
    return path.join(collect_dir, cfg['id']+ext)

def update_filenames(spec, outdir):
    for cfg in spec:
        if 'file' in cfg:
            cfg['file'] = collected_filename(cfg, outdir)
        yield cfg

def write_file(fn, text):
    with codecs.open(fn,"w",encoding="utf8") as f:
        f.write(text)

def load_spec(spec, captions=None):
    """
    Load spec from YAML or simply pass it through
    unaltered if it is already a list of mappings

    kwargs:
      captions  pass in a separate filename (or object) of pandoc
                markdown containing figure captions
    """
    try:
        with open(spec) as f:
            spec = yaml.load(f.read())
    except TypeError:
        pass

    if captions is not None:
        spec = list(integrate_captions(spec, captions))
    return spec

def update_defaults(item, **kwargs):
    """
    Updates passed configuration for figures and
    tables with default values
    """
    # We need to add a default width
    # or ability to specify one
    __ = dict(
        scale=None,
        type='figure',
        two_column=False,
        width=False,
        sideways=False,
        starred_floats=True,
        enabled=True,
        caption="",
        # If we check whether figure is referenced, we
        # can flag unused figures as such
        referenced=True)

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

    # Apply figure order if set
    order_by = kwargs.pop('order_by', None)
    if order_by is not None:
        spec = reorder_includes(order_by, spec)

    i = 0
    for item in spec:
        cfg = update_defaults(item, **kwargs)
        # Process caption
        if cfg['caption'] != "":
            cfg['caption'] = ctx.pandoc_processor(
                # This is pretty ugly, come up with a
                # better system
                figure_id_filter(cfg["caption"]))

        method = getattr(ctx.tex_renderer,"make_"+cfg['type'])
        # Get rid of disabled figures
        if not cfg['enabled']:
            continue
        i += 1
        cfg['n'] = i
        yield cfg["id"], method(cfg)

