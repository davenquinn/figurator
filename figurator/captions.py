from __future__ import print_function
from os import path
from re import compile

def parse_markdown(fobj):
    """
    Parse captions to a dict generator
    """
    key = None
    for line in fobj:
        if line.startswith("#"):
            if key is not None:
                yield key, val.rstrip()
            key = line[1:].strip()
            val = ""
        elif not line.isspace():
            val += line
    if key is not None:
        yield key, val.rstrip()

regex = compile(r'^\\section{([\w\\]+)}')

def parse_latex(fobj):
    """
    Parse captions to a dict generator
    """
    key = None
    for line in fobj:
        match = regex.match(line)
        if match:
            if key is not None:
                yield key, val.rstrip()
            key = match.group(1).replace("\\_","_")
            val = ""
        elif not line.isspace():
            val += line
    if key is not None:
        yield key, val.rstrip()

def load_captions(filename):
    """
    Loads captions from a markdown or latex document containing
    a list of captions organized by `#fig-id` headers.
    """
    parser = parse_markdown
    ext = path.splitext(filename)[1]
    if ext in ['.tex', '.latex']:
        parser = parse_latex
    with open(filename, "r") as f:
        return {k:v for k,v in parser(f)}

def integrate_captions(spec, captions):
    for cfg in spec:
        id = cfg['id']
        if id in captions:
            cfg['caption'] = captions[id]
        yield cfg

