from __future__ import print_function

def parse_captions(fobj):
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

def load_captions(obj):
    """
    Loads captions from a markdown document containing
    a list of captions organized by `#fig-id` headers.
    """
    parse = lambda f: {k:v for k,v in parse_captions(f)}
    try:
        with open(obj, "r") as f:
            return parse(f)
    except TypeError:
        return parse(obj)

def integrate_captions(spec, captions):
    captions = load_captions(captions)
    for cfg in spec:
        id = cfg['id']
        if id in captions:
            cfg['caption'] = captions[id]
        yield cfg

