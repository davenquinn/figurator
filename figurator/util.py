
def apply_defaults(kwargs, **overrides):
    defaults=dict(
        captions=None,
        collect_dir=None,
        template_dir=None,
        citation_backend='natbib',
        starred_floats=True)
    defaults.update(**overrides)
    defaults.update(**kwargs)
    return defaults

