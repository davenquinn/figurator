# -*- coding: utf-8 -*-
from shutil import copyfile
from os import path, symlink
from click import echo, secho, style
from .processors import load_spec, collected_filename

### Collection of figures ###
_file = lambda x: style(x, fg='cyan')
_bullet = lambda c: style("●",fg=c)

def find_file(file,search_paths=[]):
    for p in search_paths:
        fn = path.join(p,file)
        if path.isfile(fn):
            return fn
    raise IOError("File '{0}' not found".format(f))

def find_files(cfg, search_paths=[]):
    if cfg['files']:
        for f in cfg['files']:
            yield find_file(f)
    if cfg['file']:
        yield find_file(cfg['file'])

def resolve_figures(spec, search_paths=[]):
    spec = load_spec(spec)
    for cfg in spec:
        for f in find_files(cfg, search_paths):
            yield f

def collect_figures(spec, outdir, search_paths=[], copy=False):
    """
    Collects figures into a specific directory
    ARGS
    spec: filename of YAML figure specification or list of cfg items
    outdir: directory in which to collect figures
    search_paths: dirs in which to search for figures matching filenames
    """
    spec = load_spec(spec)

    for cfg in spec:
        try:
            fn = find_file(cfg, search_paths)
        except IOError:
            echo(_bullet('red')+" Couldn't find file "+_file(cfg['file']))
            continue
        except AttributeError:
            echo(_bullet('red')+" No file defined")
            continue

        new_fn = collected_filename(cfg,outdir)
        if path.isfile(new_fn):
            if path.getsize(fn) == path.getsize(new_fn):
                continue

        if copy:
            copyfile(fn,new_fn)
        else:
            try:
                symlink(fn,new_fn)
            except:
                echo(_bullet('yellow')+" File exists")

        # Report progress
        mode = "Copied" if copy else "Symlinked"
        echo(_bullet('green')+" "+mode+" "+_file(fn))
        pad = " "*len(mode)
        echo(pad+"to "+_file(new_fn))

    echo("Finished collecting figures")
