# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import networkx as nx
import matplotlib.pyplot as plt
from Database import Link, fetchall_links, fetchall_links_with_weight_threshold, get_destinations, get_max_weight, \
    get_avg_weight_nonzero, folder, get_count_for_destinations, slo
import Community
import numpy as np

links = fetchall_links_with_weight_threshold(1)
destinations_dict = dict()
for d in get_destinations():
    if d.destination not in destinations_dict: # tempfix todokk delete
        if d.latitude > 50000000:
            destinations_dict[d.destination] = np.array([d.longitude, d.latitude/1000000.0])
        elif d.latitude > 5000000:
            destinations_dict[d.destination] = np.array([d.longitude, d.latitude/100000.0])
        elif d.latitude > 500000:
            destinations_dict[d.destination] = np.array([d.longitude, d.latitude/10000.0])
        elif d.latitude > 50000:
            destinations_dict[d.destination] = np.array([d.longitude, d.latitude/1000.0])
        #if d.latitude > 50000:
        #    print (float(d.latitude)/(float(d.latitude)/5150.4433))/100.0
        #    destinations_dict[d.destination] = np.array([d.longitude, (d.latitude/(d.latitude/5150.4433))/100.0])
        else:
            destinations_dict[d.destination] = np.array([d.longitude, d.latitude])
# print destinations_dict


maxWeight = get_max_weight()
multi = maxWeight/1700.0
print maxWeight
#multi = 5
print "Multi:"+unicode(multi)
avg = get_avg_weight_nonzero()
print avg

outputFolder = folder + "/graphs"


def change_nodes_position(pos):
    for p in pos:
        pos[p] = destinations_dict[p]


def draw_graph1(save, consider_locations=True):
    G = nx.Graph()  # Graph, or DiGraph, MultiGraph, MultiDiGraph, etc
    #G.add_nodes_from(destinations)
    minW_array = [10, 30, 60, 100, 150, 200, 300, 400, 500, 600, 700, 900, 1300, 1600]
    if not slo:
        minW_array.append(1650)
    minW = 200
    minW_array = [i * multi for i in minW_array]
    #minW = 100
    if not save:
        minW_array = [minW]
    for minW in minW_array:
        plt.clf()
        G.clear()
        for l in links:
            if l.weight > minW:
                G.add_edge(l.destination1, l.destination2)
        pos = nx.spring_layout(G)
        if consider_locations:
            change_nodes_position(pos)
        nx.draw_networkx(G, pos, node_color='b', node_size=500)
        #print pos
        #plt.axis('off')
        figManager = plt.get_current_fig_manager()
        figManager.window.state('zoomed')
        if save:
            plt.savefig(outputFolder + "/graph1_minW="+str(minW)+".png")  # save as png
    plt.show()  # display


def draw_graph2(save, consider_locations=True):
    G = nx.Graph()
    minW_array = [i * multi for i in [30, 60, 90]]
    midW_array = [i * multi for i in [100, 150, 200]]
    maxW_array = [i * multi for i in [250, 400, 550, 700, 850]]
    if not save:
        if slo:
            minW_array = [i * multi for i in [60]]
        else:
            minW_array = [i * multi for i in [100]]
        minW_array = [i * multi for i in [60]]
        midW_array = [i * multi for i in [150]]
        maxW_array = [i * multi for i in [550]]
    for maxW in maxW_array:
        for midW in midW_array:
            for minW in minW_array:
                plt.clf()
                G.clear()
                for l in links:
                    if l.weight > minW:
                        G.add_edge(l.destination1, l.destination2, weight=l.weight)

                elarge=[(u, v) for (u, v, d) in G.edges(data=True) if d['weight'] >= maxW]
                emedium=[(u, v) for (u, v, d) in G.edges(data=True) if d['weight'] > midW and d['weight'] <maxW]
                esmall=[(u, v) for (u, v, d) in G.edges(data=True) if d['weight'] <= midW and d['weight'] > minW]
                pos = nx.shell_layout(G)  # spring, shell, circular positions for all nodes
                if consider_locations:
                    change_nodes_position(pos)
                # nodes
                nx.draw_networkx_nodes(G, pos, alpha=0.7, node_size=300)
                # edges
                nx.draw_networkx_edges(G, pos, edgelist=elarge,
                                       width=3)
                nx.draw_networkx_edges(G, pos, edgelist=emedium,
                                       width=2,alpha=0.8, edge_color='b', style='dashed')
                nx.draw_networkx_edges(G, pos, edgelist=esmall,
                                       width=1, alpha=0.2, edge_color='b', style='dashed')
                # labels
                nx.draw_networkx_labels(G, pos, font_size=15, font_family='sans-serif')
                plt.axis('off')
                figManager = plt.get_current_fig_manager()
                figManager.window.state('zoomed')
                if save:
                    plt.savefig(outputFolder + "/graph2_maxW="+str(maxW)+"_midW="+str(midW)+"_minW="+str(minW)+".png")
    plt.show()


def draw_graph3(save, consider_locations=True):
    G = nx.Graph()
    if slo:
        minW_array = [i * multi for i in [0, 10, 20, 40, 60, 100, 120, 150]]
    else:
        minW_array = [i * multi for i in [ 800]] #100, 120, 150, 200, 400]]
    maxW_array = [i * multi for i in [100, 200, 400, 600, 1000, 1300, 1500]]
    maxW_array.append(maxWeight)
    if not save:
        minW_array = [100]
        maxW_array = [1000]
    for minW in minW_array:
        for maxW in maxW_array:
            if minW >= maxW:
                continue
            plt.clf()
            G.clear()
            for l in links:
                if minW < l.weight < maxW:
                    G.add_edge(l.destination1, l.destination2, weight=l.weight)

            # use one of the edge properties to control line thickness
            edgewidth = [d['weight']/float(maxWeight/avg) for (u,v,d) in G.edges(data=True)]
            emedium = [(u, v) for (u, v, d) in G.edges(data=True) if minW < d['weight'] < maxW]
            pos=nx.spring_layout(G)  # spring, shell, circular positions for all nodes
            if consider_locations:
                change_nodes_position(pos)
            # labels
            nx.draw_networkx_labels(G, pos, font_size=14, font_family='sans-serif', alpha=0.8)
            #nx.draw_networkx_nodes(G,pos,alpha=0.6,node_size=400)
            nx.draw_networkx_edges(G, pos, edgelist=emedium,
                                   width=edgewidth, alpha=0.7)
            #labels = nx.get_edge_attributes(G,'weight')
            #nx.draw_networkx_edge_labels(G,pos,edge_labels=labels)

            #print G.neighbors("Ljubljana")
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
            colors = ['b', 'y', 'g', 'w', 'r', 'c']
            for count,i in enumerate(set(partition.values())):
                print "Community", i
                members = list_nodes = [nodes for nodes in partition.keys() if partition[nodes] == i]
                print members
                #nx.set_node_attributes(members, 'color', 'b')
                nx.draw_networkx_nodes(G,pos,
                                       nodelist=members,
                                       node_color=colors[count],
                                       node_size=400,
                                       alpha=0.75)
            # poglej še: https://networkx.github.io/documentation/stable/reference/algorithms/community.html
            plt.axis('off')
            figManager = plt.get_current_fig_manager()
            figManager.window.state('zoomed')
            if save:
                plt.savefig(outputFolder + "/graph3_minW="+str(minW)+"_maxW="+str(maxW)+".png")
    plt.show()

print get_count_for_destinations(u"Bled", u"Ljubljana")
print get_count_for_destinations(u"Bled", u"Skofljica")
#draw_graph3(True)
draw_graph3(False)
