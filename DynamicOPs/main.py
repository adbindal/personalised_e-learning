import sys
import Paths
import networkx as nx
import matplotlib.pyplot as plt

class Course:
    def __init__(self, numberOfLevels):
        self.numberOfLevels = numberOfLevels
        self.numberOfPerspectivesAtLevel = [0]*numberOfLevels
        self.numberOfLOsAtLevel = [0]*numberOfLevels
        self.maximumLAAtLevel = [0]*numberOfLevels
        self.levels = [Level(i) for i in range(numberOfLevels)]

class Level:
    def __init__(self, levelIndex):
        self.levelIndex = levelIndex
        self.vertexes = []
        
class Vertex:

    def __init__(self, levelIndex, perspectiveIndex, timeAssigned):
        self.levelIndex = levelIndex
        self.perspectiveIndex = perspectiveIndex
        self.timeAssigned = timeAssigned
        #self.subVertexes = SubVertex()[numberOfLOs]
        self.edgeList = []
        return

    def toString(self):
        return str(self.levelIndex) + ", " + str(self.perspectiveIndex)

class Edge:
    def __init__(self, destination, difficulty):
        self.destination = destination
        self.difficulty = difficulty
        return

    def toString(self):
        return self.destination.toString() + ", " + str(self.difficulty)

def readCourse(Input):
    oldin = sys.stdin
    sys.stdin = Input

    numberOfLevels = input()
    course = Course(numberOfLevels)
    course.numberOfPerspectivesAtLevel = readArray(int)
    course.numberOfLOsAtLevel = readArray(int)
    course.maximumLAAtLevel = normalize(readArray(float))
    for i in range(numberOfLevels):
        for j in range(course.numberOfPerspectivesAtLevel[i]):
            timeAssigned = input()
            course.levels[i].vertexes.append(Vertex(i, j, timeAssigned))
    for i in range(numberOfLevels):
        for j in range(course.numberOfPerspectivesAtLevel[i]):
            maxDifficulty = 0.0
            k = 0
            while i+1 < numberOfLevels and k < course.numberOfPerspectivesAtLevel[i+1]:
                difficulty = input()
                course.levels[i].vertexes[j].edgeList.append(Edge(course.levels[i+1].vertexes[k], float(difficulty)))
                maxDifficulty = max([maxDifficulty, difficulty])
                k += 1
            for edge in course.levels[i].vertexes[j].edgeList:
                edge.difficulty /= maxDifficulty
            for l in range(course.numberOfPerspectivesAtLevel[i]):
                if l != j:
                    course.levels[i].vertexes[j].edgeList.append(Edge(course.levels[i].vertexes[l], 0.0))
    sys.stdin = oldin
    return course
    

def readArray(x):
    return map(x, raw_input().split())

def normalize(array):
    sumOfElements = sum(array)
    return [Element / sumOfElements for Element in array]

def getVertices(course):
    nodeList = []
    for i in range(course.numberOfLevels):
        for j in range(course.numberOfPerspectivesAtLevel[i]):
            node = course.levels[i].vertexes[j]
            nodeList.append((node.toString(), node))
    return nodeList

def getTransition(course):
    edgeList = []
    for i in range(course.numberOfLevels):
        for j in range(course.numberOfPerspectivesAtLevel[i]):
            source = course.levels[i].vertexes[j]
            for edge in source.edgeList:
                edgeList.append((source.toString(), edge.destination.toString(), edge.difficulty))
    return edgeList

def setPosition(G):
    pos = {}
    vals = []

    # For recognizing the template of the Graph
    for i in sorted(G.nodes()):
        lvl,_ = map(int, i.split(','))
        if len(vals) > lvl:
            vals[lvl] += 1
        else:
            vals.append(1)

    # For the placcement of the Edges on Screen
    mid = (max(vals)-1)/2.0
    for i in G.nodes():
        lvl, val = map(int, i.split(','))
        pos[i] = (lvl, (-val + (vals[lvl]-1)/2.0 + mid))
    return pos
    
def create_graph(course):

    # create networkx graph
    G=nx.DiGraph()

    nodes = getVertices(course)
    edges = getTransition(course)
    nodeLabels = {}
    edgeLabels = {}
    
    # add nodes
    for id, node in nodes:
        G.add_node(id, value = node)
        nodeLabels[id] = node.timeAssigned

    # add edges
    for src, dest, wt in edges:
        if wt != 0.0: G.add_edge(src, dest, weight = (int(wt*100)/100.0))
        
    #tough = [(u,v) for (u,v,d) in G.edges(data=True) if d['weight'] != 0.0]
    edgeLabels = dict([((u,v), d['weight']) for (u,v,d) in G.edges(data=True)])

    return G, nodeLabels, edgeLabels
    
def draw_graph(G, nodeLabels = None, edgeLabels = None, pathList = None):

    # draw graph
    pos = setPosition(G)
    nx.draw_networkx_nodes(G, pos, node_size=2600, alpha= 0.9, node_color='black')
    nx.draw_networkx_edges(G, pos, width=0.5, alpha=0.9, edge_color='black', arrows=False)
    nx.draw_networkx_labels(G, pos, labels = nodeLabels, font_color='white', font_size=18)
    nx.draw_networkx_edge_labels(G, pos, edge_labels = edgeLabels, label_pos=0.4, font_size=18)
    if pathList:
        samelvl = [(u,v) for (u,v) in pathList if u[0] == v[0]]
        difflvl = [(u,v) for (u,v) in pathList if u[0] != v[0]]
        nx.draw_networkx_edges(G, pos, edgelist=samelvl, width=1.0, edge_color='red', style='dashed')
        nx.draw_networkx_edges(G, pos, edgelist=difflvl, width=1.0, edge_color='red')

    # show graph
    plt.axis('off')
    plt.show()
    return

def showProgress(G, n, e):
    Aim = "290913_peer_1.txt"
    #Aim = "../Result_current.txt"
    for path, labels in Paths.getPath(Aim):
        pathList = [(path[i-1], path[i])for i in range(1, len(path))]
        draw_graph(G, n, e, pathList)
    return  
    
# draw example
course, perspectives, transitions = create_graph(readCourse(open("input", "r")))
showProgress(course, perspectives, transitions)
