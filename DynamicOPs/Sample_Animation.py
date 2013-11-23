# For detailed comments on animation and the techniques used here, see
# http://www.scipy.org/Cookbook/Matplotlib/Animations
import sys
import time

import gtk, gobject
import matplotlib
matplotlib.use('GTKAgg')
import pylab as p

import math
import networkx as NX


def circular(G,angle):
    # circular layout of graph, rotate by angle
    n=len(G.nodes())
    tt=[(2.0*math.pi/n)*i+angle for i in range(n)]
    x=[math.cos(t) for t in tt]
    y=[math.sin(t) for t in tt]
    xy=zip(x,y)
    vpos=dict(zip(G.nodes(),xy))
    return vpos        

ax = p.subplot(111)
canvas = ax.figure.canvas

# create the initial graph drawing
G=NX.complete_graph(8)
pos=circular(G,0)
edge_collection=NX.draw_networkx_edges(G,pos,animated=True)
node_collection=NX.draw_networkx_nodes(G,pos,animated=True)

background=canvas.copy_from_bbox(ax.bbox)

def update_graph(*args):
    # restore the clean slate background
    canvas.restore_region(background)
    # update the data
    angle=2.0*math.pi*update_graph.cnt/1000.0
    update_graph.pos=circular(G,angle)
    n=NX.draw_networkx_nodes(G,update_graph.pos)
    e=NX.draw_networkx_edges(G,update_graph.pos)
    edge_collection._segments=e._segments
    node_collection._offsets=n._offsets
    # just draw the animated artist
    ax.draw_artist(edge_collection)
    ax.draw_artist(node_collection)
    # just redraw the axes rectangle
    canvas.blit(ax.bbox)
    if update_graph.cnt==200:  sys.exit()
    update_graph.cnt += 1
    return True

update_graph.cnt = 0
update_graph.pos=pos
gobject.idle_add(update_graph)

p.show()
