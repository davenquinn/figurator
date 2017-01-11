from __future__ import print_function
import click, re
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

@figures.command(name='list')
@click.argument('defs', type=_path)
@click.option('--captions',type=_path)
@click.option('--collect-dir',type=_path)
@click.option('--natbib','backend',flag_value='natbib', default=True)
@click.option('--biblatex', 'backend',flag_value='biblatex')
def figure_list(defs, captions=None, collect_dir=None, backend='natbib'):
    create_latex_figure_list(defs, captions, collect_dir, citation_backend=backend)

@figures.command(name='inline')
@click.argument('defs', type=_path)
@click.option('--captions',type=_path)
@click.option('--collect-dir',type=_path)
@click.option('--template-dir',type=_path)
@click.option('--natbib','backend',flag_value='natbib', default=True)
@click.option('--biblatex', 'backend',flag_value='biblatex')
def figure_list(defs, captions=None, collect_dir=None, template_dir=None, backend='natbib'):
    """
    A text filter to include inline figures in pandoc markdown
    Pipe text through this filter then into pandoc
    """
    stdin = click.get_text_stream('stdin')
    stdout = click.get_text_stream('stdout')
    fn = inline_figure_filter(defs, captions, collect_dir,
                template_dir=template_dir,
                citation_backend=backend)
    text = stdin.read()
    stdout.write(fn(text))
