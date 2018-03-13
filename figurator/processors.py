from __future__ import print_function
import codecs
import yaml
from os import path
from click import pass_context
from .captions import load_captions, integrate_captions
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

def load_spec(spec, caption_file=None, pandoc_processor=None):
    """
    Load spec from YAML or simply pass it through
    unaltered if it is already a list of mappings

    kwargs:
      captions  pass in a separate filename (or object) of pandoc
                markdown (with extension .md) or latex
                containing figure captions. Captions should be separated
                with section headers titled with the figure id, e.g
                #afig-id
    """
    try:
        with open(spec) as f:
            spec = yaml.load(f.read())
    except TypeError:
        pass

    if caption_file is not None:
        captions = load_captions(caption_file)
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
        # Width and scale are used to develop
        # the size
        width='20pc',
        scale=None,
        # If size is present, it takes precedence over
        # width and scale.
        size=None,
        type='figure',
        two_column=False,
        sideways=False,
        starred_floats=True,
        desc="",
        caption="",
        # If we check whether figure is referenced, we
        # can flag unused figures as such
        referenced=True,
        enabled=True)

    __.update(**item)

    __["env"] = __["type"]

    if __['two_column']:
        __['width'] = '\\textwidth'
    # Add stars to two_column floats
    # `True` by default
    # (this is useful for two-column layouts)
    if kwargs.pop("starred_floats",True):
        if __["two_column"]:
            __["env"] += "*"

    if __.get('size') is None:
        size = "width={}".format(__['width'])
        scale = __.get('scale')
        if scale is not None:
            size += ",scale={}".format(scale)
        __['size'] = size

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

    captions_file = kwargs.pop('captions', None)
    if captions_file is not None:
        captions_are_markdown = path.splitext(captions_file)[1] == '.md'
    else:
        captions_are_markdown = True

    spec = load_spec(spec,
        caption_file=captions_file)
    # We modify filenames if invoked with `collect_dir`
    collect_dir = kwargs.pop('collect_dir',None)
    if collect_dir is not None:
        spec = update_filenames(spec, collect_dir)

    spec = [update_defaults(item, **kwargs)
            for item in spec]

    # Apply figure order if set
    order_by = kwargs.pop('order_by', None)
    if order_by is not None:
        spec = reorder_includes(order_by, spec)

    # No way to turn this off in the cli yet
    ignore_disabled = kwargs.pop('ignore_disabled', True)
    i = 0 # Figure counter
    for cfg in spec:
        if ignore_disabled and not cfg['enabled']:
            continue

        def process_text_field(id):
            if cfg[id] != "":
                cfg[id] = ctx.pandoc_processor(cfg[id])

        # Process caption
        #if captions_are_markdown:
        #    process_text_field('caption')
        process_text_field('desc')

        method = getattr(ctx.tex_renderer,"make_"+cfg['type'])
        # Get rid of disabled figures
        if not cfg['enabled']:
            continue
        i += 1
        cfg['n'] = i
        yield cfg["id"], method(cfg)

