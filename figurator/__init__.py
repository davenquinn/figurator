#!/usr/bin/env python
#-*- coding: utf8 -*-

from __future__ import print_function
import yaml
import pypandoc
from shutil import copyfile
from os import path, symlink
from collections import OrderedDict
from jinja2 import Environment, FileSystemLoader
from click import echo, secho, style

from .captions import integrate_captions

def pandoc_processor(text, citation_backend='biblatex'):
    """
    Parse snippets of text as Pandoc for inclusion in
    LaTeX templates.
    """
    extra_args = None
    extra_args=["--biblatex"]
    return pypandoc.convert(text, 'latex',
            format="md", extra_args=extra_args)

__dirname = path.dirname(__file__)
templates = path.join(__dirname,"templates")

# Load file from local templates directory before
# resorting to module's templates directory
# TODO: create a configurable template directory
#       which should help with generalization
def create_tex_renderer(templates_dir):
    dirs = [
        'templates',
        templates_dir]

    e = Environment(
        block_start_string = '<#',
        block_end_string = '#>',
        variable_start_string = '<<',
        variable_end_string = '>>',
        comment_start_string = '<=',
        comment_end_string = '=>',
        loader = FileSystemLoader(dirs))

    e.filters['escape_filename'] = lambda x: x.replace(" ","\ ")
    return e

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
    __ = dict(
        scale=None,
        type='figure',
        two_column=False,
        width='20pc',
        sideways=False,
        caption="")

    if __['two_column']:
        __['width'] = '42pc'

    __.update(**item)

    __["env"] = __["type"]

    # Add stars to two_column floats
    # `True` by default
    # (this is useful for two-column layouts)
    if kwargs.pop("starred_floats",True):
        if __["two_column"]:
            __["env"] += "*"

    return __

def make_figure(data, template="figure.tex", template_dir=templates):
    # allow overriding of template from figure defs
    tmp = data.pop('template',None)
    if tmp is not None:
        template = tmp+'.tex'

    tex_renderer = create_tex_renderer(template_dir)
    fig = tex_renderer.get_template(template)
    return fig.render(**data)

def make_table(data, template="table.tex", template_dir=templates):
    # Add table notes if defined
    if 'notes' in data:
        data["notes"] = OrderedDict(sorted(data["notes"].items()))

    # Get LaTeX document that holds table body
    try:
        with open(data['file']) as f:
            data["content"] = f.read()
    except:
        data["content"] = "Cannot find table file"
    tex_renderer = create_tex_renderer(template_dir)
    table = tex_renderer.get_template(template)
    return table.render(**data)

### Collection of figures ###

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

_file = lambda x: style(x, fg='cyan')
_bullet = lambda c: style("●",fg=c)

def collect_figures(spec, outdir, search_paths=[], copy=False):
    """
    Collects figures into a specific directory
    ARGS
    spec: filename of YAML figure specification or list of cfg items
    outdir: directory in which to collect figures
    search_paths: dirs in which to search for figures matching filenames
    """
    spec = load_spec(spec)

    def __find_file(f):
        for p in search_paths:
            fn = path.join(p,f)
            if path.isfile(fn):
                return fn
        return None

    for cfg in spec:
        if not 'file' in cfg:
            continue # No file to be had

        fn = __find_file(cfg['file'])
        if fn is None:
            echo(_bullet('red')+" Couldn't find file "+_file(cfg['file']))
            continue

        new_fn = collected_filename(cfg,outdir)
        if copy:
            copyfile(fn,new_fn)
        else:
            symlink(fn,new_fn)

        # Report progress
        mode = "Copied" if copy else "Symlinked"
        echo(_bullet('green')+" "+mode+" "+_file(fn))
        pad = " "*len(mode)
        echo(pad+"to "+_file(new_fn))

### Process includes ###

methods = dict(
    figure=make_figure,
    table=make_table)

def process_includes(spec, **kwargs):
    spec = load_spec(spec,
        captions=kwargs.pop('captions', None))
    # We modify filenames if invoked with `collect_dir`
    collect_dir = kwargs.pop('collect_dir',None)
    template_dir = kwargs.pop('template_dir',templates)
    citation_backend = kwargs.pop('citation_backend','natbib')

    if collect_dir is not None:
        spec = update_filenames(spec, collect_dir)

    for item in spec:
        cfg = update_defaults(item, **kwargs)
        # Process caption
        if cfg['caption'] != "":
            cfg['caption'] = pandoc_processor(cfg["caption"], citation_backend=citation_backend)

        yield cfg["id"], methods[cfg['type']](cfg,
            template_dir=template_dir)

