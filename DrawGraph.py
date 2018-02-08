# -*- coding: utf-8 -*-
import networkx as nx
import matplotlib.pyplot as plt
from Database import Link, fetchall_links, fetchall_links_with_weight_threshold, get_destinations, get_max_weight, \
    get_avg_weight_nonzero
import Community

links = fetchall_links_with_weight_threshold(1)
destinations = get_destinations()

maxWeight = get_max_weight()
print maxWeight
avg = get_avg_weight_nonzero()
print avg


def draw_graph1(save):
    G = nx.Graph() # Graph, or DiGraph, MultiGraph, MultiDiGraph, etc
    #G.add_nodes_from(destinations)
    minW = 20
    for l in links:
        if (l.weight > minW):
            G.add_edge(l.destination1, l.destination2)
    nx.draw_networkx(G, node_color='b', node_size=500)
    plt.axis('off')
    figManager = plt.get_current_fig_manager()
    figManager.window.state('zoomed')
    if save:
        plt.savefig("data/graph1_minW="+str(minW)+".png")  # save as png
    plt.show()  # display


def draw_graph2(save):
    G = nx.Graph()

    minW = 30
    maxW = 130
    mid = 60

    for l in links:
        if l.weight > minW:
            G.add_edge(l.destination1, l.destination2, weight=l.weight)

    elarge=[(u,v) for (u,v,d) in G.edges(data=True) if d['weight'] >=maxW]
    emedium=[(u,v) for (u,v,d) in G.edges(data=True) if d['weight'] >mid and d['weight'] <maxW]
    esmall=[(u,v) for (u,v,d) in G.edges(data=True) if d['weight'] <=mid and d['weight']> minW]
    pos=nx.shell_layout(G) # spring, shell, circular positions for all nodes
    # nodes
    nx.draw_networkx_nodes(G,pos,node_size=500)
    # edges
    nx.draw_networkx_edges(G,pos,edgelist=elarge,
                           width=3)
    nx.draw_networkx_edges(G,pos,edgelist=emedium,
                           width=2,alpha=0.8,edge_color='b',style='dashed')
    nx.draw_networkx_edges(G,pos,edgelist=esmall,
                           width=1,alpha=0.2,edge_color='b',style='dashed')
    # labels
    nx.draw_networkx_labels(G,pos,font_size=15,font_family='sans-serif')
    plt.axis('off')
    figManager = plt.get_current_fig_manager()
    figManager.window.state('zoomed')
    if save:
        plt.savefig("data/graph2_minW="+str(minW)+"_midW="+str(mid)+"_maxW="+str(maxW)+".png")
    plt.show()


def draw_graph3(save):
    G = nx.Graph()

    minW = 10
    maxW = 400

    for l in links:
        if minW < l.weight < maxW:
            G.add_edge(l.destination1, l.destination2, weight=l.weight)

    # use one of the edge properties to control line thickness
    edgewidth = [ d['weight']/float(maxWeight/avg) for (u,v,d) in G.edges(data=True)]
    emedium=[(u,v) for (u,v,d) in G.edges(data=True) if d['weight'] >minW and d['weight'] <maxW]
    pos=nx.shell_layout(G) # spring, shell, circular positions for all nodes
    # labels
    nx.draw_networkx_labels(G,pos,font_size=15,font_family='sans-serif')
    nx.draw_networkx_nodes(G,pos,node_size=500)
    nx.draw_networkx_edges(G,pos,edgelist=emedium,
                           width=edgewidth,alpha=0.8)
    #labels = nx.get_edge_attributes(G,'weight')
    #nx.draw_networkx_edge_labels(G,pos,edge_labels=labels)

    print G.neighbors("Ljubljana")
    print nx.is_connected(G)
    print nx.number_connected_components(G)
    #? print G.degree("Ljubljana", weighted=False)
    #če digraph: print G.in_degree(with_labels=True)
    comps = nx.connected_component_subgraphs(G)
    for c in comps:
        print c
    ccs = nx.clustering(G)
    print ccs
    #print sum(ccs)/len(ccs)
    partition = Community.best_partition(G)
    colors = ['b','y', 'g','w','r']
    for count,i in enumerate(set(partition.values())):
        print "Community", i
        members = list_nodes = [nodes for nodes in partition.keys() if partition[nodes] == i]
        print members
        #nx.set_node_attributes(members, 'color', 'b')
        nx.draw_networkx_nodes(G,pos,
                               nodelist=members,
                               node_color=colors[count],
                               node_size=400,
                               alpha=0.9)
    # poglej še: https://networkx.github.io/documentation/stable/reference/algorithms/community.html
    plt.axis('off')
    figManager = plt.get_current_fig_manager()
    figManager.window.state('zoomed')
    if save:
        plt.savefig("data/graph3_minW="+str(minW)+"_maxW="+str(maxW)+".png")
    plt.show() # display

draw_graph1(False)
#draw_graph3(True)
