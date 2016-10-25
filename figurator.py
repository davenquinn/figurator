#!/usr/bin/env python
#-*- coding: utf8 -*-

import yaml
import pypandoc
from shutil import copyfile
from os import path, symlink
from collections import OrderedDict
from jinja2 import Environment, FileSystemLoader

def pandoc_processor(text):
    """
    Parse snippets of text as Pandoc for inclusion in
    LaTeX templates.
    """
    return pypandoc.convert(text, 'latex',
            format="md", extra_args=["--natbib"])

__dirname = path.dirname(__file__)
templates = path.join(__dirname,"templates")

# Load file from local templates directory before
# resorting to module's templates directory
# TODO: create a configurable template directory
#       which should help with generalization
dirs = [
    'templates',
    path.join(__dirname,'templates')]

tex_renderer = Environment(
    block_start_string = '<#',
    block_end_string = '#>',
    variable_start_string = '<<',
    variable_end_string = '>>',
    comment_start_string = '<=',
    comment_end_string = '=>',
    loader = FileSystemLoader(dirs))

def __load_spec(spec):
    """
    Load spec from YAML or simply pass it through
    unaltered if it is already a list of mappings
    """
    if isinstance(spec[0], dict):
        return spec
    with open(spec) as f:
        return yaml.load(f.read())

def update_defaults(item):
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
    __.update(**item)
    star = "*" if __["two_column"] else ""

    if __['two_column']:
        __['width'] = '42pc'

    __["env"] = __["type"] + star
    return __

def make_figure(data):
    if data['caption'] != "":
        data['caption'] = pandoc_processor(data["caption"])

    fig = tex_renderer.get_template("figure.tex")
    return fig.render(**data)

def make_table(data):
    data["caption"] = pandoc_processor(data["caption"])

    # Add table notes if defined
    if 'notes' in data:
        data["notes"] = OrderedDict(sorted(data["notes"].items()))

    # Get LaTeX document that holds table body
    try:
        with open(data['file']) as f:
            data["content"] = f.read()
    except:
        data["content"] = "Cannot find table file"

    table = tex_renderer.get_template("table.tex")
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

def collect_figures(spec, outdir, search_paths=[], copy=False):
    """
    Collects figures into a specific directory
    ARGS
    spec: filename of YAML figure specification or list of cfg items
    outdir: directory in which to collect figures
    search_paths: dirs in which to search for figures matching filenames
    """
    spec = __load_spec(spec)

    for cfg in spec:
        if not 'file' in cfg:
            continue # No file to be had

        for p in search_paths:
            fn = path.join(p,cfg['file'])
            if path.isfile(fn):
                break # We found our filename!

        new_fn = collected_filename(cfg,outdir)
        if copy:
            copyfile(fn,new_fn)
        else:
            symlink(fn,new_fn)

### Process includes ###

methods = dict(
    figure=make_figure,
    table=make_table)

def process_includes(spec, collect_dir=None):
    spec = __load_spec(spec)
    # We modify filenames if invoked with `collect_dir`
    if collect_dir is not None:
        spec = update_filenames(spec, collect_dir)
    for item in spec:
        cfg = update_defaults(item)
        yield methods[cfg['type']](cfg)

