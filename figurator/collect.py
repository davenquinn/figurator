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
    echo(_bullet('red')+" Couldn't find file "+_file(file), err=True)

def find_files(cfg, search_paths):
    __ = []
    if 'files' in cfg:
        __ += list(cfg['files'])
    if 'file' in cfg:
        __.append(cfg['file'])
    for file in __:
        fi = find_file(file, search_paths)
        if fi:
            yield fi

def resolve_figures(spec, search_paths=[]):
    spec = load_spec(spec)
    for cfg in spec:
        for f in find_files(cfg, search_paths):
            yield f

def relative_symlink(src, dst):
    dir_ = path.dirname(dst)
    src1 = path.relpath(src, dir_)
    dst1 = path.join(dir_, path.basename(src1))
    return symlink(src1, dst1)

def collect_figures(spec, outdir, search_paths=[], copy=False):
    """
    Collects figures into a specific directory
    ARGS
    spec: filename of YAML figure specification or list of cfg items
    outdir: directory in which to collect figures
    search_paths: dirs in which to search for figures matching filenames
    """
    secho("Collecting figures from "+_file(spec), bold=True, err=True, fg='cyan')

    spec = load_spec(spec)
    if spec is None:
        return

    for cfg in spec:
        for fn in find_files(cfg, search_paths):
            new_fn = collected_filename(cfg,outdir)
            if path.isfile(new_fn):
                if path.getsize(fn) == path.getsize(new_fn):
                    continue

            fn = path.abspath(fn)
            if copy:
                copyfile(fn,new_fn)
            else:
                try:
                    relative_symlink(fn, new_fn)
                except:
                    echo(_bullet('yellow')+" File exists", err=True)

            # Report progress
            mode = "Copied" if copy else "Symlinked"
            echo(_bullet('green')+" "+mode+" "+_file(fn), err=True)
            pad = " "*len(mode)
            echo(pad+"to "+_file(new_fn), err=True)

    echo("Finished collecting figures", err=True)
