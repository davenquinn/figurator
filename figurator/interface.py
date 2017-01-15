from click import argument, option, pass_context, Path
from functools import update_wrapper
from pypandoc import convert
from .tex_renderer import TexRenderer
from .processors import load_spec, process_includes

_path = Path(exists=True)

def standard_interface(f):
    @argument('defs', type=_path)
    @option('--captions',type=_path)
    @option('--collect-dir',type=_path,
        help="Directory in which figure files can be found by ID")
    @option('--starred-floats/--no-starred-floats', default=True)
    @option('--natbib','citation_backend',flag_value='natbib', default=True)
    @option('--biblatex', 'citation_backend',flag_value='biblatex')
    @pass_context
    def cli_wrapper(ctx, defs, **kwargs):
        # Get captions file if defined
        spec = load_spec(defs,
            captions=kwargs.pop('captions', None))

        # Create a global pandoc processor
        cb = kwargs.pop('citation_backend')
        def fn(text):
            return convert(text, 'latex',
                format="md", extra_args=["--"+cb])
        ctx.pandoc_processor = fn

        template_dir = kwargs.pop('template_dir')
        ctx.tex_renderer = TexRenderer(*template_dir)

        includes = process_includes(spec, **kwargs)
        return ctx.invoke(f, ctx, spec, includes)
    return update_wrapper(cli_wrapper, f)
