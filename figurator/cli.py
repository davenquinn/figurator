from __future__ import print_function
import click, re
from . import collect_figures
from .figure_list import create_latex_figure_list

_path = click.Path(exists=True)

@click.command()
@click.argument('defs', type=_path)
@click.argument('outdir', type=_path)
@click.argument('search_dirs', type=_path, nargs=-1)
@click.option('--copy', is_flag=True, default=False)
def collect(defs, outdir, search_dirs, copy=False):
    collect_figures(
        defs, outdir,
        search_dirs,
        copy=copy)

@click.command()
@click.argument('defs', type=_path)
@click.option('--captions',type=_path)
@click.option('--collect-dir',type=_path)
def figure_list(defs, captions=None, collect_dir=None):
    create_latex_figure_list(defs, captions, collect_dir)
