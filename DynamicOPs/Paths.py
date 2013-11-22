import networkx as nx

def getId(vertex):
    lvl, vtx, _ = vertex.split(',')
    return lvl.strip()[1] + ', ' + vtx.strip()[0]

def getLabel(vertex):
    return int(vertex.strip()[-1])

def iPath(filename):
    for line in open(filename, "r"):
        print line
        if ' ->' in line: yield line
    
def getPath(filename):
    for path in iPath(filename):
        strNodes = path.split('->')
        Nodes = []
        Labels = []
        for each in strNodes:
            Nodes.append(getId(each))
            Labels.append(getLabel(each))
        yield Nodes, Labels
    return
