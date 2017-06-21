from __future__ import print_function
import click, re
from os import path
from .collect import collect_figures, resolve_figures
from .text_filters import (
    inline_figure_filter,
    latex_figure_list,
    figure_id_filter)
from .interface import standard_interface, _path

# Setup default template directories
__dirname = path.dirname(__file__)

cli = click.Group()

def template_dir(location):
    return click.option(
        '--template-dir','-t',
        type=_path, multiple=True,
        default=[path.join(__dirname,"templates",location)],
        help="Directory containing templates (can be several)")

@cli.command(name='collect')
@click.argument('defs', type=_path)
@click.argument('collect_dir', type=_path)
@click.argument('search_dirs', type=_path, nargs=-1)
@click.option('--copy', is_flag=True, default=False)
def collect(defs, collect_dir, search_dirs, copy=False):
    collect_figures(
        defs, collect_dir,
        search_dirs,
        copy=copy)

@cli.command(name='resolve')
@click.argument('defs', type=_path)
@click.argument('search_dirs', type=_path, nargs=-1)
def resolve(defs, search_dirs):
    names = ['\"'+click.format_filename(fn)+'\"'
         for fn in resolve_figures(defs, search_dirs)]
    click.echo(" ".join(names))

@cli.command(name='list')
@template_dir("figure-list")
@standard_interface
def figure_list(ctx, defs, includes):
    outfile=click.get_text_stream('stdout')
    latex_figure_list(defs, includes, outfile)

@cli.command(name='inline')
@template_dir("generic")
@standard_interface
def inline_figures(ctx, defs, includes):
    """
    A text filter to include inline figures in pandoc markdown
    Pipe text through this filter then into pandoc

    Also includes filter to expand refs
    """
    stdin = click.get_text_stream('stdin')
    stdout = click.get_text_stream('stdout')
    fn = inline_figure_filter(defs, includes)
    text = figure_id_filter(stdin.read())
    stdout.write(fn(text))

@cli.command(name='expand-refs')
def expand_refs():
    stdin = click.get_text_stream('stdin')
    stdout = click.get_text_stream('stdout')
    text = figure_id_filter(stdin.read())
    stdout.write(text)

expand_refs.__doc__ = figure_id_filter.__doc__
