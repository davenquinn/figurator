from re import compile

__aux_pattern = compile(r'\\newlabel{((fig|tbl):(\w+))}{{(\d+)\\relax }{\d+}}')
__tex_pattern = compile(r'\\ref{((fig|tbl):(\w+))}')

def get_texfile_references(f):
    """
    Get the order of references from tex file
    """
    counter = dict(fig=0, tab=0)
    for match in __tex_pattern.finditer(f.read()):
        type = match.group(2)
        counter[type] += 1
        yield dict(
            label=match.group(1),
            type=match.group(2),
            id=match.group(3),
            num=counter[type])

def reorder_includes(order_file, includes):
    order = list(get_texfile_references(order_file))
    _includes = list(includes)
    keys = [a['id'] for a in order]
    def sortfunc(a):
        ### Sort disabled figures to the end
        if a['enabled'] == False:
            return len(keys)
        try:
            return keys.index(a['id'])
        except ValueError:
            # This would happen for unreferenced figures
            return len(keys)+1
    includes = sorted(_includes, key=sortfunc)

    for v in includes:
        # Mark unreferenced figures
        # as such.
        try:
            keys.index(v['id'])
        except ValueError:
            v['referenced'] = False
        yield v

