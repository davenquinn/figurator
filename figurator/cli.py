from __future__ import print_function
import click, re
from functools import update_wrapper
from . import collect_figures
from .figure_list import create_latex_figure_list
from .inline_figures import inline_figure_filter

_path = click.Path(exists=True)

figures = click.Group()

@figures.command(name='collect')
@click.argument('defs', type=_path)
@click.argument('collect_dir', type=_path)
@click.argument('search_dirs', type=_path, nargs=-1)
@click.option('--copy', is_flag=True, default=False)
def collect(defs, collect_dir, search_dirs, copy=False):
    collect_figures(
        defs, collect_dir,
        search_dirs,
        copy=copy)


def standard_interface(f):
    @click.argument('defs', type=_path)
    @click.option('--captions',type=_path)
    @click.option('--collect-dir',type=_path, help="Directory in which figure files can be found by ID")
    @click.option('--template-dir',type=_path, help="Directory containing templates")
    @click.option('--starred-floats/--no-starred-floats', default=True)
    @click.option('--natbib','backend',flag_value='natbib', default=True)
    @click.option('--biblatex', 'backend',flag_value='biblatex')
    @click.pass_context
    def cli_wrapper(ctx, defs, **kwargs):
        return ctx.invoke(f, ctx, defs, **kwargs)
    return update_wrapper(cli_wrapper, f)

@figures.command(name='list')
@standard_interface
def figure_list(ctx, defs, **kwargs):
    create_latex_figure_list(defs, captions=captions, collect_dir=collect_dir,
        starred_floats=starred_floats, citation_backend=backend)

@figures.command(name='inline')
@standard_interface
def figure_list(ctx, defs, **kwargs):
    """
    A text filter to include inline figures in pandoc markdown
    Pipe text through this filter then into pandoc
    """
    stdin = click.get_text_stream('stdin')
    stdout = click.get_text_stream('stdout')
    fn = inline_figure_filter(defs, **kwargs)
    text = stdin.read()
    stdout.write(fn(text))
