from re import compile

__aux_pattern = compile(r'\\newlabel{((fig|tab):(\w+))}{{(\d+)\\relax }{\d+}}')
def get_auxfile_references(f):
    """
    Get the order of references from auxfiles
    """
    counter = dict(fig=0, tab=0)
    for line in f:
        match = __aux_pattern.match(line)
        if match is None: continue
        type = match.group(2)
        counter[type] += 1
        yield dict(
            label=match.group(1),
            type=match.group(2),
            id=match.group(3),
            num=counter[type])

def reorder_includes(order_file, includes):
    order = list(get_auxfile_references(order_file))
    includes = list(includes)
    keys = [a['id'] for a in order]
    def sortfunc(a):
        try:
            return keys.index(a['id'])
        except ValueError:
            return len(keys)
    includes = sorted(includes, key=sortfunc)
    for v in includes:
        # Mark unreferenced figures
        # as such.
        try:
            keys.index(v['id'])
        except ValueError:
            v['referenced'] = False
        yield v

