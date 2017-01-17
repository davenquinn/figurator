from __future__ import print_function
from jinja2 import Environment, FileSystemLoader
from pandas import isnull
from collections import OrderedDict

# Filters for pandoc renderer

def nominal(value,rounding=2):
    if isnull(value):
        return '--'
    fs = "{0:."+str(rounding)+"f}"
    try:
        return fs.format(value.n)
    except AttributeError:
        return fs.format(value)

def uncertain(value,rounding=2):
    fs = "{0:."+str(rounding)+"f}"
    d = tuple(fs.format(i)\
        for i in (value.n, value.s))
    try:
        return "$\pm$".join(d)
    except AttributeError:
        return value

# Load file from local templates directory before
# resorting to module's templates directory
# TODO: create a configurable template directory
#       which should help with generalization
class TexRenderer(Environment):
    def __init__(self, *template_dirs):
        dirs = list(template_dirs)
        dirs.append('templates')
        Environment.__init__(self,
            block_start_string = '<#',
            block_end_string = '#>',
            variable_start_string = '<<',
            variable_end_string = '>>',
            comment_start_string = '<=',
            comment_end_string = '=>',
            loader = FileSystemLoader(dirs))

        self.filters["un"] = uncertain
        self.filters["n"] = nominal

    def make_figure(self, data, template="figure.tex"):
        # allow overriding of template from figure defs
        tmp = data.pop('template',None)
        if tmp is not None:
            template = tmp+'.tex'

        fig = self.get_template(template)
        return fig.render(**data)

    def make_table(self, data, template="table.tex"):
        # Add table notes if defined
        if 'notes' in data:
            data["notes"] = OrderedDict(sorted(data["notes"].items()))

        # Get LaTeX document that holds table body
        try:
            with open(data['file']) as f:
                data["content"] = f.read()
        except:
            data["content"] = "Cannot find table file"
        table = self.get_template(template)
        return table.render(**data)
