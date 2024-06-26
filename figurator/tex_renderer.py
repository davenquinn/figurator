from __future__ import print_function

from collections import OrderedDict
from os.path import abspath

from click import echo, style
from jinja2 import Environment, FileSystemLoader

# Filters for pandoc renderer


def isnull(value):
    """Instead of using Pandas isnull, we use our own"""
    if value is None:
        return True
    if isinstance(value, str):
        return value == ""
    if isinstance(value, (list, tuple)):
        return len(value) == 0
    if isinstance(value, dict):
        return len(value) == 0
    return False


def nominal(value, rounding=2):
    if isnull(value):
        return "--"
    fs = "{0:." + str(rounding) + "f}"
    try:
        return fs.format(value.n)
    except AttributeError:
        return fs.format(value)
    except TypeError:
        return fs.format(value)


def uncertain(value, rounding=2):
    fs = "{0:." + str(rounding) + "f}"
    d = tuple(fs.format(i) for i in (value.n, value.s))
    try:
        return "$\pm$".join(d)
    except AttributeError:
        return value


def escape(value):
    return value.replace("_", "{\_}")


def uncertain_parenthetical(value, rounding=2):
    fstring = "{0:." + str(rounding) + "uS}"
    try:
        s = fstring.format(value)
    except ValueError:
        s = str(value) + "()"
    return s.replace("(", "~(")


def filter_by_fstring(value, fstring="{}"):
    tries = [
        lambda x: fstring.format(x),
        lambda x: fstring.format(*x),
        lambda x: fstring.format(**x),
    ]
    for fn in tries:
        try:
            return fn(value)
        except:
            pass


# Load file from local templates directory before
# resorting to module's templates directory
# TODO: create a configurable template directory
#       which should help with generalization
class TexRenderer(Environment):
    def __init__(self, *template_dirs):
        dirs = list(template_dirs)
        dirs += ["templates"]
        Environment.__init__(
            self,
            block_start_string="<#",
            block_end_string="#>",
            variable_start_string="<<",
            variable_end_string=">>",
            comment_start_string="<=",
            comment_end_string="=>",
            loader=FileSystemLoader(dirs),
        )

        self.filters["f"] = filter_by_fstring
        self.filters["un"] = uncertain
        self.filters["n"] = nominal
        self.filters["escape"] = escape
        self.filters["unp"] = uncertain_parenthetical

    def make_figure(self, data, template="figure.tex"):
        # allow overriding of template from figure defs
        tmp = data.pop("template", None)
        if tmp is not None:
            template = tmp + ".tex"

        fig = self.get_template(template)
        return fig.render(**data)

    def make_table(self, data, template="table.tex"):
        # Add table notes if defined
        if "notes" in data:
            data["notes"] = OrderedDict(sorted(data["notes"].items()))
        tmp = data.pop("template", None)
        if tmp is not None:
            template = tmp + ".tex"

        fn = abspath(data["file"])
        if fn.endswith(".pdf"):
            tbl = self.get_template("pdf-table.tex")
            return tbl.render(**data)

        # Get LaTeX document that holds table body
        try:
            with open(fn) as f:
                data["content"] = f.read()
        except:
            echo("Cannot find table file " + style(fn, fg="red"), err=True)
            data["content"] = "Cannot find table file " + fn
        table = self.get_template(template)
        return table.render(**data)
