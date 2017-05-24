from click import argument, option, pass_context, Path, File
from functools import update_wrapper, partial
from pypandoc import convert
from .tex_renderer import TexRenderer
from .processors import load_spec, process_includes

_path = Path(exists=True)

def pandoc_processor(text, citation_backend=None, extra_args=[]):
    if citation_backend is not None:
        extra_args.append("--"+citation_backend)
    return convert(text, 'latex', format='md',
        extra_args=extra_args)

def standard_interface(f):
    @argument('defs', type=_path)
    @option('--captions',type=_path)
    @option('--collect-dir',type=_path,
        help="Directory in which figure files can be found by ID")
    # This is kinda a legacy option -- this type of thing can be controlled by
    # pointing to a new set of templates now.
    @option('--starred-floats/--no-starred-floats', default=True)
    @option('--natbib','citation_backend',flag_value='natbib', default=True)
    @option('--biblatex', 'citation_backend',flag_value='biblatex')
    @option("--order-by", default=None, type=File())
    @pass_context
    def cli_wrapper(ctx, defs, **kwargs):
        # Get captions file if defined
        spec = load_spec(defs,
            captions=kwargs.pop('captions', None))

        # Create a global pandoc processor
        ctx.pandoc_processor = partial(
            pandoc_processor,
            citation_backend=kwargs.pop('citation_backend'))

        template_dir = kwargs.pop('template_dir')
        ctx.tex_renderer = TexRenderer(*template_dir)

        includes = process_includes(spec, **kwargs)
        return ctx.invoke(f, ctx, spec, includes)
    return update_wrapper(cli_wrapper, f)
