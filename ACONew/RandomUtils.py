import sys, random, re
import StaticACO, ObjectiveFunction

def getDouble():
    " Get a random double number "
    return random.random()

def getInt(limit):
    " Get a random int x such that 0 <= x < limit "
    return random.randint(0, limit-1)

def getLong(limit):
    " Get a random long int x such that 0 <= x < limit "
    return random.randint(0, limit-1)

def getRange(low, high):
    " Get a random int x such that low <= x <= high "
    return random.randint(low, high)

def getAttributes(node):
    print node
    src, dest, lo = re.split(",", node)
    digits = "0123456789"
    getn = lambda s: ''.join([i for i in s if i in digits])
    print src, dest, lo
    s, d = getn(src), getn(dest)
    vertex = tuple([int(s), int(d)])
    LO = int(lo)
    return vertex, LO

def createPathObject(sPath):
    newPath = StaticACO.Path()
    nodes = re.split("->", sPath)
    print nodes
    
    # --- Add Dummy vertex --- #
    dummy = StaticACO.Vertex(-1, -1, 0, 0)
    dummy.edgeList.append(StaticACO.Edge(getAttributes(nodes[0]), 0))
    newPath.add(dummy, 0)
    # ------------------------ #

    for node in nodes:
        v, l = getAttributes(node)
        newPath.add(v, l)

    return newPath
