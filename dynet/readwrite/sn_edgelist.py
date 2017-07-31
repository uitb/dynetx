from networkx.utils import open_file, make_str
from dynet.classes.sngraph import SNGraph

__author__ = 'Giulio Rossetti'
__license__ = "GPL"
__email__ = "giulio.rossetti@gmail.com"

__all__ = ['generate_sn_edgelist',
           'write_sn_edgelist',
           'parse_sn_edgelist',
           'read_sn_edgelist']


def generate_sn_edgelist(G, delimiter=' '):

    for u, v, d in G.edges(data=True):

        if 'time' not in d:
            raise NotImplemented
        for t in d['time']:
            e = [u, v, t]

            try:
                e.extend(d[k] for k in d if k != "time" and k != "pres")
            except KeyError:
                pass
            yield delimiter.join(map(make_str, e))


@open_file(1, mode='wb')
def write_sn_edgelist(G, path, delimiter=' ',  encoding='utf-8'):

    for line in generate_sn_edgelist(G, delimiter):
        line += '\n'
        path.write(line.encode(encoding))


def parse_sn_edgelist(lines, comments='#', delimiter=None, create_using=None, nodetype=None, timestamptype=None):
    if create_using is None:
        G = SNGraph()
    else:
        try:
            G = create_using
            G.clear()
        except:
            raise TypeError("create_using input is not a DyNet graph type")

    for line in lines:
        p = line.find(comments)
        if p >= 0:
            line = line[:p]
        if not len(line):
            continue
        # split line, should have 2 or more
        s = line.strip().split(delimiter)
        if len(s) < 3:
            continue
        u = s.pop(0)
        v = s.pop(0)
        t = s.pop(0)

        if nodetype is not None:
            try:
                u = nodetype(u)
                v = nodetype(v)
            except:
                raise TypeError("Failed to convert nodes %s,%s to type %s." %(u, v, nodetype))

        if timestamptype is not None:
            try:
                t = timestamptype(t)
            except:
                raise TypeError("Failed to convert timestamp %s to type %s." % (t, nodetype))

        G.add_edge(u, v, attr_dict={'time': t})
    return G


@open_file(0,mode='rb')
def read_sn_edgelist(path, comments="#", delimiter=None, create_using=None,
                  nodetype=None, timestamptype=None, encoding='utf-8'):

    lines = (line.decode(encoding) for line in path)
    return parse_sn_edgelist(lines,comments=comments, delimiter=delimiter, create_using=create_using, nodetype=nodetype,
                             timestamptype=timestamptype)


# fixture for nose tests
def teardown_module(module):
    import os
    for fname in ['test.sn_edgelist', 'test.sn_edgelist.gz']:
        if os.path.isfile(fname):
            os.unlink(fname)
