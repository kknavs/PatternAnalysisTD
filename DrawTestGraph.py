# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import networkx as nx
import matplotlib.pyplot as plt
from Database import Link, fetchall_links, fetchall_links_with_weight_threshold, get_destinations, get_max_weight, \
    get_avg_weight_nonzero, folder, get_count_for_destinations, get_max_link_weight, DataType, selectedData
import community_louvain as Community
import numpy as np
from networkx.algorithms import community as community_nx
import itertools
from operator import itemgetter
from FilterGraph import Season, generate_graph, generate_graph_for_destination, get_fname
# https://github.com/taynaud/python-louvain/tree/networkx2
# pip install -U git+https://github.com/taynaud/python-louvain.git@networkx2

links = fetchall_links_with_weight_threshold(1)
destinations_dict = dict()
for d in get_destinations():
    print d
    if d.destination not in destinations_dict:
        destinations_dict[d.destination] = np.array([d.longitude, d.latitude])
print len(destinations_dict)


maxWeight = get_max_weight()
multi = maxWeight/1700.0
multi *= 1.1
if selectedData == DataType.VIENNA:
    multi = (maxWeight*10)/1700
for d in get_max_link_weight():
    print d
print maxWeight
#multi = 5
print "Multi:"+unicode(multi)
avg = get_avg_weight_nonzero()
print avg
colors = ['b', 'y', 'g', 'w', 'r', 'c']

outputFolder = folder + "/graphs"


def change_nodes_position(pos):
    for p in pos:
        pos[p] = destinations_dict[p]


def draw_graph1(save, consider_locations=True):
    G = nx.Graph()  # Graph, or DiGraph, MultiGraph, MultiDiGraph, etc
    #G.add_nodes_from(destinations)
    minW_array = [10, 30, 60, 100, 150, 200, 300, 400, 500, 600, 700, 900, 1300, 1600]
    if selectedData != DataType.SLO:
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
        if selectedData == DataType.SLO:
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


def draw_louvain(save=True, consider_locations=True,filters=None, season=Season.ALL):
    plt.clf()
    G = generate_graph(filters=filters, season=season)
    print(nx.info(G))
    #nx.draw_networkx_nodes(G, pos=pos, nodelist=G.nodes)

    # use one of the edge properties to control line thickness
    edgewidth = [d['weight']/float(maxWeight/avg) for (u,v,d) in G.edges(data=True)]
    #edgewidth = [d['weight']/float(avg) for (u,v,d) in G.edges(data=True)]
    emedium = [(u, v) for (u, v, d) in G.edges(data=True)]
    pos=nx.spring_layout(G)  # spring, shell, circular positions for all nodes
    if consider_locations:
        change_nodes_position(pos)
    # labels
    nx.draw_networkx_labels(G, pos, font_size=13, alpha=0.8)
    #nx.draw_networkx_nodes(G,pos,alpha=0.6,node_size=400)
    nx.draw_networkx_edges(G, pos, edgelist=emedium,
                           width=edgewidth, alpha=0.7)
    print nx.is_connected(G)
    print nx.number_connected_components(G)
    comps = nx.connected_component_subgraphs(G)
    print "Comps"
    for c in comps:
        print c
    ccs = nx.clustering(G)
    print ccs
    #print sum(ccs)/len(ccs)
    # print nx.__version__  is 2.1
    partition = Community.best_partition(G, None, 'weight')
    for count,i in enumerate(set(partition.values())):
        print "Community", i
        members = list_nodes = [nodes for nodes in partition.keys() if partition[nodes] == i]
        print members
        #nx.set_node_attributes(members, 'color', 'b')
        nx.draw_networkx_nodes(G,pos,
                               nodelist=members,
                               node_color=colors[count],
                               node_size=350,
                               alpha=0.75)
    plt.axis('off')
    figManager = plt.get_current_fig_manager()
    #figManager.window.state('zoomed')
    if save:
        plt.savefig(outputFolder + "/louvain/louvain_"+get_fname(filters,season)+".png")

#    plt.show()

filters_arr = [{"user_hometown_country": ["Slovenia"]},
               {"user_hometown_country": ["United Kingdom"]},
               {"user_hometown_country": ["United States"]},
               {"user_hometown_country": ["Italy"]},
               {"user_hometown_country": ["Croatia"]},
               {"user_hometown_country": ["Austria"]},
               {"user_hometown_country": ["Hungary"]}]
for filters in filters_arr:
    draw_louvain(filters=filters, save=True)

def draw_graph3(save, consider_locations=True):
    G = nx.Graph()
    if selectedData == DataType.SLO:
        minW_array = [i * multi for i in [0, 10, 20, 40, 60, 100, 120, 150]]
    else:
        minW_array = [100, 120, 150, 200, 400, 800, 1000]
    maxW_array = [i * multi for i in [100, 200, 400, 600, 1000, 1300, 1500]]
    maxW_array.append(maxWeight)
    if not save:
        minW_array = [100 * multi]
        maxW_array = [maxWeight+100]
    for minW in minW_array:
        for maxW in maxW_array:
            if minW >= maxW:
                continue
            plt.clf()
            G.clear()
            for l in links:
                if minW < l.weight < maxW:
                    G.add_edge(l.destination1, l.destination2, weight=l.weight) #obr?

            # use one of the edge properties to control line thickness
            edgewidth = [d['weight']/float(maxWeight/avg) for (u,v,d) in G.edges(data=True)]
            #edgewidth = [d['weight']/float(avg) for (u,v,d) in G.edges(data=True)]
            emedium = [(u, v) for (u, v, d) in G.edges(data=True)]
            pos=nx.spring_layout(G)  # spring, shell, circular positions for all nodes
            if consider_locations:
                change_nodes_position(pos)
            # labels
            nx.draw_networkx_labels(G, pos, font_size=13, font_family='sans-serif', alpha=0.8)
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
            print "Comps"
            for c in comps:
                print c
            ccs = nx.clustering(G)
            print ccs
            #print sum(ccs)/len(ccs)
            # print nx.__version__  is 2.1
            partition = Community.best_partition(G, None, 'weight')
            for count,i in enumerate(set(partition.values())):
                print "Community", i
                members = list_nodes = [nodes for nodes in partition.keys() if partition[nodes] == i]
                print members
                #nx.set_node_attributes(members, 'color', 'b')
                nx.draw_networkx_nodes(G,pos,
                                       nodelist=members,
                                       node_color=colors[count],
                                       node_size=350,
                                       alpha=0.75)
            # poglej še: https://networkx.github.io/documentation/stable/reference/algorithms/community.html
            plt.axis('off')
            figManager = plt.get_current_fig_manager()
            figManager.window.state('zoomed')
            if save:
                plt.savefig(outputFolder + "/louvain/graph3_minW="+str(minW)+"_maxW="+str(maxW)+".png")
    plt.show()


def draw_graph4(save, consider_locations=True):
    G = nx.Graph()
    N_groups = 3
    colors = ['b', 'y', 'g', 'w', 'r', 'c']
    if selectedData == DataType.SLO:
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
            sliding = float(len(pos))/N_groups
            print sliding
            # labels
            nx.draw_networkx_labels(G, pos, font_size=13, font_family='sans-serif', alpha=0.8)
            #nx.draw_networkx_nodes(G,pos,alpha=0.6,node_size=400)
            nx.draw_networkx_edges(G, pos, edgelist=emedium,
                                   width=edgewidth, alpha=0.7)
            for count in range(N_groups):
                print "Group", count
                members = set([nodes for c, nodes in enumerate(pos) if count*sliding <= c < (count+1)*sliding])
                print members
                nx.draw_networkx_nodes(G,pos,
                                       nodelist=members,
                                       node_color=colors[count],
                                       node_size=350,
                                       alpha=0.75)
            plt.axis('off')
            figManager = plt.get_current_fig_manager()
            figManager.window.state('zoomed')
            if save:
                plt.savefig(outputFolder + "/graph4_minW="+str(minW)+"_maxW="+str(maxW)+".png")
    plt.show()


def draw_graph5(save, consider_locations=True):
    G = nx.Graph()
    N_groups = 4
    colors = ['b', 'y', 'g', 'w', 'r', 'c']
    if selectedData == DataType.SLO:
        minW_array = [i * multi for i in [0, 10, 20, 40, 60, 100, 120, 150]]
    else:
        minW_array = [i * multi for i in [ 800]] #100, 120, 150, 200, 400]]
    maxW_array = [i * multi for i in [100, 200, 400, 600, 1000, 1300, 1500]]
    maxW_array.append(maxWeight)
    if not save:
        minW_array = [120] #[100]
        maxW_array = [maxWeight+1] #[1000]
    for minW in minW_array:
        for maxW in maxW_array:
            if minW >= maxW:
                continue
            plt.clf()
            G.clear()
            for l in links:
                if minW < l.weight < maxW:
                    G.add_edge(l.destination1, l.destination2, weight=l.weight) #/float(maxWeight/avg))
                    #G.add_node(l.destination1, node_color='g', node_size=400, alpha=0.75)
            #edgewidth = [d['weight']/float(maxWeight/avg) for (u, v, d) in G.edges(data=True)]
            #print edgewidth
            pos=nx.spring_layout(G)  # spring, shell, circular positions for all nodes
            if consider_locations:
                change_nodes_position(pos)
                # use one of the edge properties to control line thickness
            #for a, b, data in sorted(G.edges(data=True), key=lambda x: x[2]['weight']):
            sorted_edges = sorted(G.edges(data=True), key=lambda x: x[2]['weight'])
            print sorted_edges
            edgewidth = [d['weight'] for (u, v, d) in sorted_edges]
            print edgewidth
            emedium = [(u, v) for (u, v, d) in sorted_edges]
            sliding = float(len(emedium))/N_groups #maxWeight/N_groups
            print str("Sliding:")+str(sliding)
            # labels
            nx.draw_networkx_labels(G, pos, font_size=14, font_family='sans-serif', alpha=0.8)
            allMembers = set()
            edgeColors = []
            for count in range(N_groups):
                print "Group", count
                listMembers = [nodes for c, nodes in enumerate(emedium) if count*sliding <= c < (count+1)*sliding]
                print listMembers
                #edgeMembers = set(listMembers)
                #print edgeMembers
                members = set([nodes[0] for nodes in listMembers])
                members = members.union(set([nodes[1] for nodes in listMembers]))
                members = members.difference(allMembers)
                print members
                #allMembers = allMembers.union(members)

                nx.draw_networkx_nodes(G,pos,
                                       nodelist=members,
                                       node_color=colors[count],
                                       node_size=200,
                                       alpha=0.75)
                edgeColors +=[str(colors[count])]*len(listMembers)
                print edgeColors
            #edgeColors = [colors[int(floor(d/sliding))] for d in edgewidth]
            edgewidth = [15*d['weight']/float(maxWeight) for (u, v, d) in sorted_edges]
            nx.draw_networkx_edges(G, pos, width=edgewidth, egdelist=emedium, alpha=0.6, edge_color=edgeColors)
            #nx.draw_networkx_edges(G, pos, edgelist=emedium, width=edgewidth, alpha=0.7,
            #                       width=edgewidth, alpha=0.7)
            plt.axis('off')
            figManager = plt.get_current_fig_manager()
            figManager.window.state('zoomed')
            if save:
                plt.savefig(outputFolder + "/graph5_minW="+str(minW)+"_maxW="+str(maxW)+".png")
    plt.show()


def draw_graph6(save, consider_locations=True):
    # https://networkx.github.io/documentation/stable/reference/algorithms/community.html
    # networkx community test
    G = nx.Graph()
    #G = nx.barbell_graph(5, 1)
    minW_array = [10, 30, 60, 100, 150, 200, 300, 400, 500, 600, 700, 900, 1300, 1600]
    if selectedData != DataType.SLO:
        minW_array.append(1650)
    minW = 200
    minW_array = [i * multi for i in minW_array]
    counts = [1,2,3,4,5]
    #minW = 100
    if not save:
        minW_array = [minW]
        counts = [3]
    for minW in minW_array:
        for count in counts:
            plt.clf()
            G.clear()
            for l in links:
                if l.weight > minW:
                    G.add_edge(l.destination1, l.destination2)
            pos = nx.spring_layout(G)
            if count > len(pos): #k must be greater than graph size.
                continue
            if consider_locations:
                change_nodes_position(pos)
            # labels
            #nx.draw_networkx_labels(G, pos, font_size=15, font_family='sans-serif')
            nx.draw_networkx(G, pos, node_color='b', node_size=350)
            #nx.draw(G)
            # print nx.__version__  is 2.1
            communities_generator = community_nx.asyn_fluidc(G, count) #girvan_newman(G)
            for c in range(count):
            #top_level_communities = next(communities_generator)
            #print top_level_communities
            #members = set([nodes for c, nodes in enumerate(pos) if count*sliding <= c < (count+1)*sliding])
            #print members
            #nx.draw_networkx_nodes(G,pos,
            #                       nodelist=top_level_communities,
            #                       node_color=colors[0],
            #                       node_size=400,
            #                       alpha=0.75)
                next_level_communities = next(communities_generator)
                nx.draw_networkx_nodes(G,pos,
                                       nodelist= next_level_communities,
                                       node_color=colors[c],
                                       node_size=350,
                                       alpha=0.9)
                print next_level_communities
                sorted(map(sorted, next_level_communities))
            plt.axis('off')
            figManager = plt.get_current_fig_manager()
            figManager.window.state('zoomed')
            if save:
                plt.savefig(outputFolder + "/graph6_minW="+str(minW)+"_count="+str(count)+".png")

            """K5 = nx.convert_node_labels_to_integers(G,first_label=2)
            G.add_edges_from(K5.edges())
            c = list(community_nx.k_clique_communities(G, 4))
            print c"""
            # https://stackoverflow.com/questions/20063927/overlapping-community-detection-with-igraph-or-other-libaries
    plt.show()


def draw_graph_asyn_lpa(save, consider_locations=True):  # looks very random
    G = nx.Graph()
    if selectedData == DataType.SLO:
        minW_array = [i * multi for i in [0, 10, 20, 40, 60, 100, 120, 150]]
    else:
        minW_array = [i * multi for i in [ 800]] #100, 120, 150, 200, 400]]
    maxW_array = [i * multi for i in [100, 200, 400, 600, 1000, 1300, 1500]]
    maxW_array.append(maxWeight)
    if not save:
        minW_array = [10]
        maxW_array = [maxWeight+100]
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
            edgewidth = [d['weight']/float(maxWeight)*10 for (u,v,d) in G.edges(data=True)]
            emedium = [(u, v) for (u, v, d) in G.edges(data=True)]
            pos=nx.spring_layout(G)  # spring, shell, circular positions for all nodes
            if consider_locations:
                change_nodes_position(pos)
            nx.draw_networkx(G, pos, node_color='b', node_size=300)
            communities_generator = community_nx.asyn_lpa_communities(G, 'weight')
            c = 0
            dict_groups = {}
            while True:
                #top_level_communities = next(communities_generator)
                #print top_level_communities
                #members = set([nodes for c, nodes in enumerate(pos) if count*sliding <= c < (count+1)*sliding])
                #print members
                next_level_communities = next(communities_generator, None)
                if not next_level_communities:
                    break
                for n in next_level_communities:
                    dict_groups[n] = c
                print unicode(next_level_communities)
                c += 1
            values = [dict_groups.get(node, 0.25) for node in G.nodes()]
            nx.draw_networkx_nodes(G,pos,
                                   node_color=values,
                                   cmap=plt.cm.Set1,
                                   node_size=350,
                                   alpha=0.9)
            plt.axis('off')
            figManager = plt.get_current_fig_manager()
            figManager.window.state('zoomed')
            if save:
                plt.savefig(outputFolder + "/graph_asyn_lpa_minW="+str(minW)+"_maxW="+str(maxW)+".png")
    plt.show()


def heaviest(G):
    u, v, w = max(G.edges(data='weight'), key=itemgetter(2))
    return (u, v)


def draw_graph_girvan_newman(save, consider_locations=True):
    G = nx.Graph()
    if selectedData == DataType.SLO:
        minW_array = [i * multi for i in [0, 10, 20, 40, 60, 100, 120, 150]]
    else:
        minW_array = [i * multi for i in [ 800]] #100, 120, 150, 200, 400]]
    maxW_array = [i * multi for i in [100, 200, 400, 600, 1000, 1300, 1500]]
    maxW_array.append(maxWeight)
    if not save:
        minW_array = [100]
        maxW_array = [maxWeight+100]
    for minW in minW_array:
        for maxW in maxW_array:
            if minW >= maxW:
                continue
            plt.clf()
            G.clear()
            for l in links:
                if minW < l.weight < maxW:
                    G.add_edge(l.destination1, l.destination2, weight=l.weight)

            print "Heaviest:"+str(heaviest(G))
            # use one of the edge properties to control line thickness
            edgewidth = [d['weight']/float(maxWeight/avg) for (u,v,d) in G.edges(data=True)]
            emedium = [(u, v) for (u, v, d) in G.edges(data=True)]
            pos=nx.spring_layout(G)  # spring, shell, circular positions for all nodes
            if consider_locations:
                change_nodes_position(pos)
            k = 10
            comp = community_nx.girvan_newman(G, most_valuable_edge=heaviest)
            limited = itertools.takewhile(lambda c: len(c) <= k, comp)
            # To stop getting tuples of communities once the number of communities
            # is greater than *k*, use :func:`itertools.takewhile`::
            """>>> import itertools
            >>> G = nx.path_graph(8)
            >>> k = 4
            >>> comp = girvan_newman(G)
            >>> limited = itertools.takewhile(lambda c: len(c) <= k, comp)
            >>> for communities in limited:
            ...     print(tuple(sorted(c) for c in communities)) # doctest: +SKIP"""
            nx.draw_networkx_labels(G, pos, font_size=13, font_family='sans-serif', alpha=0.8)
            nx.draw_networkx_edges(G, pos, width=edgewidth, egdelist=G.edges, alpha=0.6)
            for communities in limited:
                dict_groups = {}
                c = 0
                print communities
                for com in (tuple(sorted(cm) for cm in communities)):
                    for n in com:
                        dict_groups[n] = c
                    print unicode(com)
                    c += 1
                values = [dict_groups.get(node, 0.25) for node in G.nodes()]
                nx.draw_networkx_nodes(G,pos,
                                       node_color=values,
                                       cmap=plt.cm.Set1,  # Blues modra shema
                                       node_size=350,
                                       alpha=0.9)
            plt.axis('off')
            figManager = plt.get_current_fig_manager()
            figManager.window.state('zoomed')
            if save:
                plt.savefig(outputFolder + "/graph_girvan_newman_minW="+str(minW)+"_maxW="+str(maxW)+".png")
    plt.show()


def draw_graph_k_clique(save, consider_locations=True):
    G = nx.Graph()
    if selectedData == DataType.SLO:
        minW_array = [i * multi for i in [0, 10, 20, 40, 60, 100, 120, 150]]
    else:
        minW_array = [i * multi for i in [ 800]] #100, 120, 150, 200, 400]]
    maxW_array = [i * multi for i in [100, 200, 400, 600, 1000, 1300, 1500]]
    maxW_array.append(maxWeight)
    if not save:
        minW_array = [10]
        maxW_array = [maxWeight+100]
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
            edgewidth = [d['weight']/float(maxWeight)*10 for (u,v,d) in G.edges(data=True)]
            emedium = [(u, v) for (u, v, d) in G.edges(data=True)]
            pos=nx.spring_layout(G)  # spring, shell, circular positions for all nodes
            if consider_locations:
                change_nodes_position(pos)
            # some are in no generated communities
            nx.draw_networkx_edges(G, pos, width=edgewidth, egdelist=G.edges, alpha=0.6)
            nx.draw_networkx_nodes(G,  pos, with_lables=False, node_color=(1,1,1),alpha=0.2, node_size=300)
            nx.draw_networkx_labels(G, pos, font_size=13, font_family='sans-serif', alpha=0.8)

            #K5 = nx.convert_node_labels_to_integers(G,first_label=2)
            #G.add_edges_from(K5.edges())
            communities_generator = community_nx.k_clique_communities(G, 3, cliques=nx.find_cliques(G))
            c = 0
            dict_groups = {}
            while True:
                #top_level_communities = next(communities_generator)
                #print top_level_communities
                next_level_communities = next(communities_generator, None)
                if not next_level_communities:
                    break
                print unicode(next_level_communities)
                for n in next_level_communities:
                    dict_groups[n] = c
                c += 1
            values = [dict_groups.get(node, 0.25) for node in dict_groups.keys()]
            nx.draw_networkx_nodes(G,pos,
                                   nodelist=dict_groups.keys(),
                                   node_color=values,
                                   cmap=plt.cm.Set1,
                                   node_size=350,
                                   alpha=0.9)
            plt.axis('off')
            figManager = plt.get_current_fig_manager()
            figManager.window.state('zoomed')
            if save:
                plt.savefig(outputFolder + "/graph_k_clique_minW="+str(minW)+"_maxW="+str(maxW)+".png")
    plt.show()


def draw_kernighan_lin_bisection(save, consider_locations=True):
    G = nx.Graph()
    if selectedData == DataType.SLO:
        minW_array = [i * multi for i in [0, 10, 20, 40, 60, 100, 120, 150]]
    else:
        minW_array = [i * multi for i in [ 800]] #100, 120, 150, 200, 400]]
    maxW_array = [i * multi for i in [100, 200, 400, 600, 1000, 1300, 1500]]
    maxW_array.append(maxWeight)
    if not save:
        minW_array = [10]
        maxW_array = [maxWeight+100]
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
            emedium = [(u, v) for (u, v, d) in G.edges(data=True)]
            pos=nx.spring_layout(G)  # spring, shell, circular positions for all nodes
            if consider_locations:
                change_nodes_position(pos)
            nx.draw_networkx(G, pos, node_color='b', node_size=300)
            # kernighan_lin_bisection(G, partition=None, max_iter=10, weight='weight'):
            a,b = community_nx.kernighan_lin_bisection(G, weight='weight')
            nx.draw_networkx_nodes(G,pos,
                                   nodelist= a,
                                   node_color='r',
                                   node_size=350,
                                   alpha=0.9)
            nx.draw_networkx_nodes(G,pos,
                                   nodelist= b,
                                   node_color='b',
                                   node_size=350,
                                   alpha=0.9)
            plt.axis('off')
            figManager = plt.get_current_fig_manager()
            figManager.window.state('zoomed')
            if save:
                plt.savefig(outputFolder + "/graph_kernighan_lin_minW="+str(minW)+"_maxW="+str(maxW)+".png")
    plt.show()


if selectedData == DataType.SLO:
    print get_count_for_destinations(u"Bled", u"Ljubljana")
    print get_count_for_destinations(u"Bled", u"Skofljica")
# 175 mW
#print get_count_for_destinations(u"British Museum", u"London Underground")  # 13  325 (no fids?, username)
#print get_count_for_destinations(u"British Museum", u"The London Eye")  # 10  386 (no fids?, username)
#draw_graph3(False)
#draw_graph_asyn_lpa(False)
#draw_graph_girvan_newman(False)
#draw_graph_k_clique(False)
#draw_kernighan_lin_bisection(False)


