from __future__ import print_function
from os import path
from re import compile
from click import echo

def parse_markdown(fobj):
    """
    Parse captions to a dict generator
    """
    key = None
    val = ""
    for line in fobj:
        if line.startswith("##"):
            if key is not None:
                yield key, val.rstrip()
            key = line[1:].strip()
            val = ""
        elif not line.isspace():
            val += line
    if key is not None:
        yield key, val.rstrip()

regex = compile(r'^\\subsection{([\w\\\-]+)}')

def parse_latex(fobj):
    """
    Parse captions to a dict generator
    """
    key = None
    val = ""
    for line in fobj:
        match = regex.match(line)
        if match:
            if key is not None:
                yield key, val.rstrip()
            key = match.group(1).replace("\\_","_")
            val = ""
        elif line.startswith("\hypertarget"):
            continue
        elif not line.isspace():
            val += line
    if key is not None:
        yield key, val.rstrip()

def load_captions(filename):
    """
    Loads captions from a markdown or latex document containing
    a list of captions organized by `##fig-id` subheaders.
    The first header will be ignored.
    """
    parser = parse_markdown
    ext = path.splitext(filename)[1]
    if ext in ['.tex', '.latex']:
        parser = parse_latex
    with open(filename, "r") as f:
        return {k:v for k,v in parser(f)}

def integrate_captions(spec, captions):
    if spec is None:
        return
    for cfg in spec:
        try:
            id = cfg['id']
        except TypeError:
            echo(f"Error integrating caption {cfg}", err=True)
            continue
        if id in captions:
            cfg['caption'] = captions[id]
        yield cfg

