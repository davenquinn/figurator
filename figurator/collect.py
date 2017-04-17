# -*- coding: utf-8 -*-
from shutil import copyfile
from os import path, symlink
from click import echo, secho, style
from .processors import load_spec, collected_filename

### Collection of figures ###
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
        # if path.isfile(new_fn):
            # if path.getsize(fn) == path.getsize(new_fn):
                # continue

        if copy:
            copyfile(fn,new_fn)
        else:
            symlink(fn,new_fn)

        # Report progress
        mode = "Copied" if copy else "Symlinked"
        echo(_bullet('green')+" "+mode+" "+_file(fn))
        pad = " "*len(mode)
        echo(pad+"to "+_file(new_fn))
