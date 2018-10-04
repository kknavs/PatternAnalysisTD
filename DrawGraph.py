# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import os
import subprocess
import community_louvain as Community

from Database import fetchall_links_with_weight_threshold, get_destinations, get_destinations_id_asc, get_max_weight, \
    folder, DataType, selectedData, get_avg_weight_nonzero
from FilterGraph import Season, generate_graph, generate_graph_for_destination, get_fname, filter_graph_by_weight


# INFOMAP building on WIN: with cygwin - cannot be run in normal cmd, with mingw + msys can be, but problems building
# C:\MinGW\infomap-master\interfaces\python  - build failing...
# INFOMAP: c:\cygwin64\bin\python2.7.exe  C:\Users\Karmen\Downloads\infomap-master\examples\python\example-simple.py


def get_infomap_executable_path():
    """
    Change path to program built from Infomap source code. It is called within subprocess.
    """
    if os.name == 'posix':  # mac
        return r"/Users/karmen/Downloads/infomap-master/Infomap"
    return r"c:/Users\Karmen\Downloads\infomap-master\Infomap.exe"  # win


# https://github.com/mapequation/infomap
# in cygwin: run make on root, then also in examples/python
# example: https://github.com/mapequation/infomap/blob/master/examples/python/infomap-examples.ipynb
# http://www.mapequation.org/code.html#Link-list-format

# On the main menu, choose File | Project Structure (or click projectStructure, or press Ctrl+Shift+Alt+S
# https://stackoverflow.com/questions/1811691/running-an-outside-program-executable-in-python

#subprocess.check_call(([r"c:\cygwin64\bin\python2.7.exe",
#                        "c:/Users\Karmen\Downloads\infomap-master\examples\python\example-simple.py"]))

# plt.switch_backend('QT4Agg')
mapping = {"Gorje":"Blejski Vintgar"}
back_mapping = {"Blejski Vintgar":"Gorje"}

maxWeight = get_max_weight()
multi = maxWeight/1700.0
multi *= 1.1
#if selectedData == DataType.VIENNA:
#    multi = (maxWeight)/1700
outputFolder = folder + "/graphs"
links = fetchall_links_with_weight_threshold(1)
avg = get_avg_weight_nonzero()
destinations_dict = dict()
ids_dict = dict()
for d in get_destinations():
    if d.destination not in destinations_dict:
        destinations_dict[d.destination] = d
        ids_dict[d.id] = d.destination
        if d.destination in mapping:
            new_k = mapping[d.destination]
            destinations_dict[new_k] = d
            ids_dict[d.id] = new_k
print "Count all destinations: ", len(destinations_dict)
print "MaxWeight: ", maxWeight


def relabel_destination(G, pos=None, back=False):
    if selectedData == DataType.SLO:
        if back:
            mapping_t = back_mapping
        else:
            mapping_t = mapping
        if not pos:
            nx.relabel_nodes(G, mapping_t, False)
        else:
            if set(mapping_t.keys()).issubset(set(pos)):
                nx.relabel_nodes(G, mapping_t, False)
                for k, v in mapping_t.iteritems():
                    pos[v] = pos[k]
                    del pos[k]  # delete old key


def draw_labels(G, pos, font_size=13, font_color='black'):
    relabel_destination(G, pos)
    nx.draw_networkx_labels(G, pos, font_size=font_size, font_color=font_color, alpha=0.8)  # font_family='sans-serif' can be defined


def change_nodes_position(pos):
    for p in pos:
        d = destinations_dict[p]
        pos[p] = np.array([d.longitude, d.latitude])


def check_available_fonts():  # sans-serif on win, Microsoft Sans Serif on mac ...
    import matplotlib
    avail_font_names = [f.name for f in matplotlib.font_manager.fontManager.ttflist]
    for f in avail_font_names:
        print f


def get_node_size(G):
    d = nx.degree(G)
    d = [(d[node]+1) * 10 for node in G.nodes()]


def draw_infomap_graph(G, minW, count_nodes, filters=None, save=False, consider_locations=True, season=Season.ALL,
                       recursion_count=0, with_markov_time=False):
    txt_name = ("/infomap/infomap_minW="+str(float(minW)/maxWeight)+"_"+get_fname(filters, season)+
                "_nodes=" + str(count_nodes)+".net").replace(" ", "_")
    if recursion_count > 0:
        txt_name = ("/infomap/infomap_minW="+str(float(minW)/maxWeight)+"_"+get_fname(filters,season) +
                    "_nodes=" + str(count_nodes)+"_rec="+str(recursion_count)+".net").replace(" ", "_")
    markov_time = 0.75
    if with_markov_time:
        txt_name = ("/infomap/infomap_minW="+str(float(minW)/maxWeight)+"_"+get_fname(filters,season) +
                    "_nodes=" + str(count_nodes)+"_markov="+str(markov_time)+".net").replace(" ", "_")
    with open(outputFolder+txt_name, str('w')) as f:
        # Pajek format (more info in FilterGraph)
        newline = str("\n")  # linux
        f.write(str("*Vertices ") + str(len(G.nodes()))+newline)
        c = 1
        temp_v = {}
        #relabel_destination(G)
        for d in get_destinations_id_asc():
            # G.add_node(d.destination)  # if all nodes added we have problems because of looping?
            if d.destination in G.nodes():
                if d.destination in mapping:
                    dest = mapping[d.destination]
                    temp_v[d.destination] = c
                else:
                    dest = d.destination
                f.write(str(c)+str(' "'+dest+'"'+newline))
                temp_v[dest] = c
                c += 1  # must follow a consequitive order.
        f.write(str("*Edges ") + str(len(G.edges()))+newline)
        for l in G.edges(data=True):
            if True:
                id1 = temp_v[l[0]]
                id2 = temp_v[l[1]]
                e_weight = G[l[0]][l[1]]['weight']
                f.write(str(str(id1)+' '+str(id2)+' '+str(e_weight)+newline))
                # we write edges in Link list format

    out_path = os.path.dirname(os.path.abspath(__file__))+"/"+outputFolder+"/infomap"
    runp = get_infomap_executable_path()
    mode = "/overlapping"
    avg =get_avg_weight_nonzero()
    avg = 0 #0.3 #0.95
    print "avg",avg
    if with_markov_time:
        subprocess.check_call([runp,
                               outputFolder+txt_name,
                               out_path + mode, "-N 20", "--undirected", "--weight-threshold "+str(avg),"--overlapping", "--bftree", "--markov-time "+str(markov_time)])
        subprocess.check_call([runp,
                               outputFolder+txt_name,
                               out_path+ mode, "-N 20", "--undirected", "--weight-threshold "+str(avg), "--overlapping",  "--tree", "--markov-time "+str(markov_time)])
    else:
        subprocess.check_call([runp,
                               outputFolder+txt_name,
                               out_path + mode, "-N 20", "--undirected", "--weight-threshold "+str(avg),"--overlapping", "--bftree"])
        subprocess.check_call([runp,
                               outputFolder+txt_name,
                               out_path+ mode, "-N 20", "--undirected", "--weight-threshold "+str(avg), "--overlapping",  "--tree"])
    # --preferred-number-of-modules 4
    # --overlapping
    plt.clf()
    dict_groups = {}
    """Tree format
    The resulting hierarchy will be written to a file with the extension .tree (plain text file) and corresponds
     to the best hierarchical partition (shortest description length) of the attempts.
     to the best hierarchical partition (shortest description length) of the attempts.
     The output format has the pattern:
    
    # Codelength = 3.48419 bits.
    1:1:1 0.0384615 "7" 6
    1:1:2 0.0384615 "8" 7
    1:1:3 0.0384615 "9" 8
    1:2:1 0.0384615 "4" 3
    1:2:2 0.0384615 "5" 4
    ...
    Each row (except the first one, which summarizes the result) begins with the
    multilevel module assignments of a node. The module assignments are colon separated from coarse to fine
    level, and all modules within each level are sorted by the total flow (PageRank) of the nodes they contain.
    Further, the integer after the last colon is the rank within the finest-level module, the decimal number is
    the amount of flow in that node, i.e. the steady state population of random walkers, the content within
    quotation marks is the node name, and finally, the last integer is the index of the node in
    the original network file."""
    with open(out_path+mode+txt_name.replace("infomap/","").replace('.net','.tree'), str('rU')) as f: # Universal newline mode
        for line in f:
            if line[0] != '#':
                print line.strip()
                l = line.strip().split('"')
                print l
                modules, flow_amount = l[0].strip().split(" ")
                node_name = l[1]
                # modules, flow_amount, node_name, ind = line.strip().split(" ")
                #  too many values to unpack - presledki v imenih
                #node_name = l[2][1:-1]
                dict_groups[node_name] = float(modules.split(":")[0])

    for n in G.nodes():
        print n, dict_groups.get(n)

    pos = nx.spring_layout(G)  # spring, shell, circular positions for all nodes
    if consider_locations:
        change_nodes_position(pos)
    draw_labels(G, pos)
    values = [dict_groups.get(node, 0.25) for node in G.nodes()]

    edgewidth = [d['weight']*15 for (u, v, d) in G.edges(data=True)]
    nx.draw_networkx_edges(G, pos, width=edgewidth, egdelist=G.edges, alpha=0.6)
    nx.draw_networkx_nodes(G,pos,
                           node_color=values,
                           cmap=plt.cm.Set1,
                           node_size=350,
                           alpha=0.9)
    plt.axis('off')
    figManager = plt.get_current_fig_manager()
    if os.name != 'posix':  # mac
        figManager.window.state('zoomed')
    if save:
        plt.savefig(outputFolder +
                    txt_name.replace(".net", ".png"))

    print nx.info(G)


    # uncomment if you want to test setting the modules - seems that setting modules makes singletons
    """ 
    txt_name = ("/infomap/infomap_minW="+str(float(minW)/maxWeight)+"_"+get_fname(filters,season)+ \
               "_nodes="+ str(count_nodes)+".net").replace(" ","_")
    out_path = os.path.dirname(os.path.abspath(__file__))+"/"+outputFolder+"/N10/infomap" #+txt_name.replace(".txt", "_out.txt")
    modules = len(G.nodes())/2
    if modules > 10:
        modules = 10
    subprocess.check_call([runp,
                       outputFolder+txt_name,
                       out_path, "-N 10", "--preferred-number-of-modules "+unicode(modules), "--overlapping",  "--bftree"])
    subprocess.check_call([runp,
                           outputFolder+txt_name,
                           out_path, "-N 10", "--preferred-number-of-modules "+unicode(modules), "--overlapping",  "--tree"])
    with open(outputFolder+"/N10"+txt_name.replace('.net','.tree'), str('rU')) as f:  # Universal newline mode
        for line in f:
            if line[0] != '#':
                print line.strip()
                l = line.strip().split('"')
                print l
                modules, flow_amount = l[0].strip().split(" ")
                node_name = l[1]
                dict_groups[node_name] = float(modules.split(":")[0])
    for n in G.nodes():
        print n, dict_groups.get(n)
    pos = nx.spring_layout(G)  # spring, shell, circular positions for all nodes
    if consider_locations:
        change_nodes_position(pos)
    plt.clf()
    draw_labels(G, pos)
    edgewidth = [d['weight']*10 for (u,v,d) in G.edges(data=True)]
    nx.draw_networkx_edges(G, pos, width=edgewidth, egdelist=G.edges, alpha=0.6)
    values = [dict_groups.get(node, 0.25) for node in G.nodes()]
    nx.draw_networkx_nodes(G,pos,
                           node_color=values,
                           cmap=plt.cm.Set1,
                           node_size=350,
                           alpha=0.9)
    plt.axis('off')
    figManager = plt.get_current_fig_manager()
    if os.name != 'posix':  # mac
        figManager.window.state('zoomed')
    if save:
        plt.savefig(outputFolder +"/N10"+
                    txt_name.replace(".net", ".png"))
    """

    # --preferred-number-of-modules 4
    # --overlapping
    if not save:
        plt.show()  # display
    relabel_destination(G, pos, back=True)
    if recursion_count < 0:  # change if you want to test
        G_first_group = nx.Graph()
        for n in G.nodes():
            print n, dict_groups.get(n)
            if dict_groups.get(n) == 1:
                for nn in G.neighbors(n):
                    if dict_groups.get(nn) == 1:
                        G_first_group.add_edge(n, nn, weight=G[n][nn]["weight"])
        print "Eliminated: ", set(G.nodes().keys()).difference(G_first_group.nodes().keys())
        #G_first_group.remove_node("Ljubljana")
        #G_first_group.remove_node("Bled")
        #G_first_group.remove_node("Zagreb")
        #G_first_group.remove_node("Gorje")
        draw_infomap_graph(G_first_group, minW, count_nodes, filters, save, consider_locations, season,
                      recursion_count+1)


def load_infomap_graph(filters=None, save=True, consider_locations=False, season=Season.ALL, with_markov_time=False):
    """
    Draw graph and communities found by Infomap.
    Parameters:
      filters - dict {filter_name :[filter_value ...]}, which filters to apply (default: None)
      save - save graph to image .png
      consider_locations - consider latitude and longitude of destination when drawing
      season - filter by time (default: any time in year)
      with_markov_time - bool, force smaller communities (default: False)
    """
    G = nx.Graph()
    if selectedData == DataType.SLO:
        minW_array = [1]#[500/float(maxWeight)]#40, 300[i * multi for i in [1, 10, 20, 40, 60, 100, 120, 150, 180, 200, 270, 300]]
    else:
        minW_array = [1]
    if with_markov_time:
        minW_array = [0,3]
    maxW_array = [] #[i * multi for i in [400]]#[i * multi for i in [100, 300, 500, 700, 1000]]
    #if selectedData == DataType.VIENNA:
    #    maxW_array +=[ 1300, 1500]
    maxW_array.append(maxWeight+1)
    #if not save:
    #    minW_array = [10 * multi]
    #   #maxW_array = [maxWeight+100]
    #    maxW_array = [1300]
    count_nodes = 0
    for minW in minW_array:
        for maxW in maxW_array:
            if minW >= maxW:
                continue
            G.clear()
            g_tmp = generate_graph(filters, False, season)

            # filter based on minW and maxW
            for destination1, destination2, nw in g_tmp.edges(data=True):
                if minW <= nw['weight'] < maxW:
                    count_nodes += nw['weight']*2
                    G.add_edge(destination1, destination2, weight=float(nw['weight'])/maxWeight)
            if len(G.nodes()) == 0:
                continue
            draw_infomap_graph(G, minW, count_nodes, filters, save, consider_locations, season,
                               with_markov_time=with_markov_time)
    # --preferred-number-of-modules 4
    # --overlapping

#load_infomap_graph(save=True)
filters_arr = [#{" age": ["13-17", "18-24"]},
               #{" age": ["35-49", "50-64"]},
              # {" age": ["65+"]},
    #{" age": ["35-49"]},
               #{" travel_style": ["Family Vacationer"]} ,
               #{" travel_style": ["Nightlife Seeker"]},
               #{" travel_style": ["History Buff"]},
               #{" travel_style": ["Backpacker"]}
    #{" travel_style": ["Peace and Quiet Seeker"]},
    #{" travel_style": ["Thrill Seeker"]},
    #{" travel_style": ["Nature Lover"]},
    #{" travel_style": ["Luxury Traveler"]},
    #{" travel_style": ["Art and Architecture Lover"]},
    #{" travel_style": ["Shopping Fanatic"]},
    #{" travel_style": ["Nightlife Seeker"]},
    #{" travel_style": ["60+ Traveler"]},
    #{" travel_style": ["Family Vacationer"]},
    #{" travel_style": ["Backpacker"]},
    #{" travel_style": ["Peace and Quiet Seeker"]},
    #{" travel_style": ["Luxury Traveler"], " age": ["65+"]},
    #{" travel_style": ["Urban Explorer"]},
    {" travel_style": ["Thrifty Traveler"]},
    {" travel_style": ["Foodie"]},
               ]

#for f in filters_arr:
#    load_infomap_graph(filters=f, save=True)


def draw_graph_for_destination(destination, save=True, filters=None, season=Season.ALL, known_locations=None):
    draw_graph_for_destination([destination], save, filters, season, known_locations)


def draw_graph_for_destinations(destinations, save=True, filters=None, season=Season.ALL, known_locations=None):

    nodes = []
    pos = dict()
    nodesize =[]
    for d in destinations:
        t_nodes, t_pos, t_nodesize = generate_graph_for_destination(d, filters=filters, season=season)
        nodes.extend(t_nodes)
        pos.update(t_pos)
        nodesize.extend(t_nodesize)
    #print(nx.info(G))
    G = nx.Graph()
    plt.clf()
    nx.draw_networkx_nodes(G, pos=pos,  node_size=nodesize, nodelist=nodes, node_color='c')
    draw_labels(G, pos)
    if known_locations:
        nx.draw_networkx_nodes(G, pos=known_locations,  node_size=60, nodelist=known_locations.keys(), node_color='orange')
        labels = dict()
        for k in known_locations.keys():
            labels[k] = k
        nx.draw_networkx_labels(G, known_locations, font_size=9, labels=labels, font_color='black')


    figManager = plt.get_current_fig_manager()
    if os.name != 'posix':  # mac
        figManager.window.state('zoomed')
    if save:
        plt.savefig(outputFolder + "/" + destinations + "/_" + get_fname(filters, season) +
                    "_nodes=" + str(len(pos)) +".png")
    plt.show()


known_locations_bled = {"Blejsko jezero": np.array([14.0938053, 46.363598]),
                   "Blejski grad": np.array([14.100680, 46.369874])}
#draw_graph_for_destination("Bled", False, known_locations=known_locations)
# Bled: izstopa Reka Hiša spodaj levo

known_locations_ljubljana = {"Ljubljanski grad": np.array([14.508374, 46.048885]),
                   "Prešernov trg": np.array([14.5062441, 46.0515696]),
                   "Koseški bajer": np.array([14.469114, 46.067308]),
                   "Živalski vrt": np.array([14.472088, 46.052740])}
                   #"Šmarna Gora": np.array([14.491390, 46.128666]),
f ={"user_hometown_country": ["Slovenia"]}
#draw_graph_for_destination("Ljubljana", True, filters=None, known_locations=known_locations, season=Season.NEW_YEAR)


filters_arr =[
#       {"gender": ["F"]},
#         {"gender": ["M"]},
          {"age": ["1", "2"]},    {"age": ["3"]},
          {"age": ["4","5"]},   {"age": ["6"]}]
"""
    {"user_travel_style": ["60+ Traveler"]},
    {"user_travel_style": ["Family Vacationer"]},
    {"user_travel_style": ["Backpacker"]},
    {"user_travel_style": ["Peace and Quiet Seeker"]},
    {"user_travel_style": ["History Buff"]},

    {"user_travel_style": ["Luxury Traveler"]},
    {"user_travel_style": ["Art and Architecture Lover"]},
    {"user_travel_style": ["Shopping Fanatic"]},
    {"user_travel_style": ["Nightlife Seeker"]},"""

filters_arr =[
    {"user_travel_style": ["60+ Traveler"]},
    {"user_travel_style": ["Family Vacationer"]},
    {"user_travel_style": ["Backpacker"]},
    {"user_travel_style": ["Peace and Quiet Seeker"]},
    {"user_travel_style": ["History Buff"]},

    {"user_travel_style": ["Luxury Traveler"]},
    {"user_travel_style": ["Art and Architecture Lover"]},
    {"user_travel_style": ["Shopping Fanatic"]},
    {"user_travel_style": ["Nightlife Seeker"]},
    {"user_travel_style": ["Luxury Traveler"], "age": ["3"]},
    {"user_travel_style": ["Art and Architecture Lover"], "age": ["3"]},
    {"user_travel_style": ["Shopping Fanatic"], "age": ["3"]},
    {"user_travel_style": ["Nightlife Seeker"], "age": ["3"]},
    {"user_travel_style": ["Luxury Traveler"], "age": ["2"]},
    {"user_travel_style": ["Art and Architecture Lover"], "age": ["2"]},
    {"user_travel_style": ["Shopping Fanatic"], "age": ["2"]},
    {"user_travel_style": ["Nightlife Seeker"], "age": ["2"]},

    {"user_travel_style": ["Luxury Traveler"], "age": ["6"]},
    {"user_travel_style": ["Art and Architecture Lover"], "age": ["6"]},
    {"user_travel_style": ["Shopping Fanatic"], "age": ["6"]},
    {"user_travel_style": ["Nightlife Seeker"], "age": ["6"]},

]
"""filters_arr = [{"user_hometown_country": ["Slovenia"]},
               {"user_hometown_country": ["United Kingdom"]},
               {"user_hometown_country": ["United States"]},
               {"user_hometown_country": ["Italy"]},
               {"user_hometown_country": ["Germany"]},
               {"user_hometown_country": ["Croatia"]},
               {"user_hometown_country": ["Austria"]},
               {"user_hometown_country": ["Hungary"]}]"""

filters_arr =[{"age": ["1","2"]}, {"age": ["3","4"]}, {"age": ["5","6"]}]

#for filters in filters_arr:
#    load_infomap_graph(filters=filters)
#filter = {"user_hometown_country": ["Italy"]}
#load_infomap_graph(save=False)


"""load_infomap_graph(save=True)
load_infomap_graph(save=True, season=Season.SUMMER)
load_infomap_graph(save=True, season=Season.WINTER)
load_infomap_graph(save=True, season=Season.NEW_YEAR)
load_infomap_graph(save=True, season=Season.WINTER_WITHOUT_NEW_YEAR)"""


def draw_louvain(save=True, consider_locations=False,filters=None, season=Season.ALL, with_resolution=False):
    """
    Draw graph and communities found by Louvain.
    Parameters:
      save - save graph to image .png
      consider_locations - consider latitude and longitude of destination when drawing
      filters - dict {filter_name :[filter_value ...]}, which filters to apply (default: None)
      season - filter by time (default: any time in year)
      with_resolution - bool, force smaller communities (default: False)
    """
    colors = ['c', 'yellow', 'lightgreen', 'pink', 'lightcoral', 'gray', 'b', 'darkorange', 'green', 'purple', 'maroon', 'c']
    font_colors = ['b', 'darkorange', 'green', 'purple', 'maroon', 'black', 'c', 'yellow', 'lightgreen', 'pink', 'lightcoral', 'b']
    plt.clf()
    G = generate_graph(filters=filters, season=season)
    min_w = 1 # 372
    if with_resolution:
        min_w = 20 #10
    G = filter_graph_by_weight(G, min_weight=min_w)
    print(nx.info(G))
    #nx.draw_networkx_nodes(G, pos=pos, nodelist=G.nodes)
    # use one of the edge properties to control line thickness
    pos=nx.spring_layout(G)  # spring, shell, circular positions for all nodes
    relabel_destination(G,pos)
    edgewidth = [d['weight']/float(maxWeight/avg) for (u,v,d) in G.edges(data=True)]
    #edgewidth = [d['weight']/float(avg) for (u,v,d) in G.edges(data=True)]
    emedium = [(u, v) for (u, v, d) in G.edges(data=True)]
    if consider_locations:
        change_nodes_position(pos)
    # labels
    #nx.draw_networkx_labels(G, pos, font_size=13, alpha=0.8)
    #nx.draw_networkx_nodes(G,pos,alpha=0.6,node_size=400)
    nx.draw_networkx_edges(G, pos, edgelist=emedium,
                           width=edgewidth, alpha=0.7)
    #print nx.is_connected(G)
    print nx.number_connected_components(G)
    comps = nx.connected_component_subgraphs(G)
    #print "Comps"
    #for c in comps:
    #    print c
    ccs = nx.clustering(G)
    print ccs
    #print sum(ccs)/len(ccs)
    # print nx.__version__  is 2.1
    mapping = dict(zip(G.nodes(), range(1, len(G.nodes()))))
    if with_resolution:
        partition = Community.best_partition(G, None, 'weight', 0.5)
    else:
        partition = Community.best_partition(G, None, 'weight')
    for count,i in enumerate(set(partition.values())):
        print "Community", i
        members = sorted([str(nodes) for nodes in partition.keys() if partition[nodes] == i])
        print members
        mapping = dict(zip(members, members))
        #nx.set_node_attributes(members, 'color', 'b')
        nx.draw_networkx_nodes(G,pos,
                               nodelist=members,
                               node_color=colors[count],
                               node_size=350,
                               alpha=0.75)
        nx.draw_networkx_labels(G, pos, labels=mapping, font_size=13, font_color=font_colors[count], alpha=0.8)

        for k in members:
            mapping.pop(k, None)
    plt.axis('off')
    figManager = plt.get_current_fig_manager()
    #figManager.window.state('zoomed')
    if save:
        plt.savefig(outputFolder + "/louvain/louvain_"+get_fname(filters,season)+".png")
    print "%:", min_w/float(maxWeight)
    plt.show()

#draw_louvain()
#load_infomap_graph(save=False)
#for filters in filters_arr:
#    draw_louvain(filters=filters, save=True)
#generate_graph(refresh=True)
#draw_louvain(save=False)


# ****** generating images for the thesis ********

def draw_greedy(num, size, greedy=False):  # num_cliques, clique_size)
    G = nx.Graph()
    for n1,n2 in [(0, 1), (1, 2), (2, 3), (0, 3),
                  (1, 4),
                  (4, 5), (5, 6), (6, 7), (4, 7),
                  (2, 8), (7, 8), (8, 9), (2, 9), (7, 9), (8, 9)]:
        G.add_edge(n1,n2)
    G = generate_graph()
    min_w = 150# 20#10 ali 20 #372
    G = filter_graph_by_weight(G, min_weight=min_w)
    """for n1,n2 in [(0, 1), (1, 2), (2, 3), (0, 3),
                  (1, 4),
                  (4, 5), (5, 6), (6, 7), (4, 7),
                  (2, 8), (7, 8), (8, 9), (2, 9), (7, 9), (8, 9)]:
        G.add_edge(n1,n2)"""
    #G = nx.ring_of_cliques(num, size)
    #G = nx.balanced_tree(2, 3)

    #nx.draw(G)
    pos = nx.spring_layout(G)
    nx.draw_networkx_edges(G, pos, G.edges())

    dict_groups = {}

    if greedy:
        dict_groups = Community.best_partition(G, None)
        #nx.draw(G,pos, node_size=700)
        print dict_groups
    else:
        txt_name = "/infomap_test.net"
        with open(outputFolder+txt_name, 'w') as f:
            # add nodes and edges to txt and graph
            # A network in Pajek format
            print G.edges()
            newline = str("\n")  # linux
            f.write(str("*Vertices ") + str(len(G.nodes()))+newline)
            c =1
            temp_v = {}
            for n in G.nodes():
                f.write(str(n)+str(' "'+str(n)+'"'+newline))
                temp_v[n] = c
                c += 1  # must follow a consequitive order.
            f.write(str("*Edges ") + str(len(G.edges()))+newline)
            for g in G.edges():
                f.write(str(str(g[0])+' '+str(g[1]))+newline)
        import os
        out_path = os.path.dirname(os.path.abspath(__file__))+"/"+outputFolder
        runp = get_infomap_executable_path()
        subprocess.check_call([runp,
                               outputFolder+txt_name,
                               out_path, "-N 10", "--tree", "-z --zero-based-numbering"])
        # --preferred-number-of-modules 4
        # --overlapping
        with open(outputFolder+txt_name.replace('.net','.tree'), 'rU') as f: # Universal newline mode
            for line in f:
                if line[0] != '#':
                    print line.strip()
                    l = line.strip().split('"')
                    print l
                    modules, flow_amount = l[0].strip().split(" ")
                    node_name = int(l[1])
                    dict_groups[node_name] = float(modules.split(":")[0])

        for n in G.nodes():
            print n, dict_groups.get(n)

    values = [dict_groups.get(node, 0.25) for node in G.nodes()]
    nx.draw_networkx_nodes(G,pos,
                           node_color=values,
                           cmap=plt.cm.Set1,
                           node_size=350,
                           alpha=1.0)


    from networkx.algorithms import community as community_nx
    #groups = [partition.get(node, 0.25) for node in G.nodes()]
    #modulariry = community_nx.modularity(G, [])
    figManager = plt.get_current_fig_manager()
    #if os.name != 'posix':  # mac
    #    figManager.window.state('zoomed')
    plt.axis('off')
    plt.show()

    #print "The modularity of the network is %f" % modularity

def draw_test_di_graph(louvain=False):
    """G = nx.DiGraph(directed=True)
    G.add_edges_from(
        [('A', 'B'), ('C', 'B'), ('C', 'D'), ('A', 'D'), ('A', 'E'),
         ('F', 'E'), ('F', 'G'), ('H', 'G'), ('H', 'E')])

    val_map ={} #{'A': 1.0,'B': 1.0,'': 1.0,'C': 1.0,'D': 1.0    }

    values = [val_map.get(node, 0.25) for node in G.nodes()]

    nx.draw(G, cmap = plt.get_cmap('jet'), node_color = values)
    plt.show()"""
    G = nx.DiGraph()
    """G.add_edges_from(
        [('0', '1'), ('2', '1'), ('2', '3'), ('0', '3'), ('0', '4'),
         ('5', '4'), ('5', '6'), ('7', '6'), ('7', '4')])"""
    G.add_edges_from(
        [('0', '1'), ('1', '2'), ('2', '3'), ('3', '0'), ('0', '4'),
         ('4', '5'), ('5', '6'), ('6', '7'), ('7', '4')])
    #G = nx.ring_of_cliques(num, size)
    #G = nx.balanced_tree(2, 3)

    #nx.draw(G)
    pos = nx.spring_layout(G)
    dict_groups = {}

    if louvain:
        dict_groups = Community.best_partition(G, None)
        #nx.draw(G,pos, node_size=700)
        print dict_groups
    else:
        txt_name = "/infomap_test.net"
        with open(outputFolder+txt_name, 'w') as f:
            # add nodes and edges to txt and graph
            # A network in Pajek format
            print G.edges()
            newline = str("\n")  # linux
            f.write(str("*Vertices ") + str(len(G.nodes()))+newline)
            c =1
            temp_v = {}
            for n in sorted(G.nodes()):
                f.write(str(n)+str(' "'+str(n)+'"'+newline))
                temp_v[n] = c
                c += 1  # must follow a consequitive order.
            f.write(str("*Edges ") + str(len(G.edges()))+newline)
            for g in G.edges():
                f.write(str(str(g[0])+' '+str(g[1]))+newline)
        out_path = os.path.dirname(os.path.abspath(__file__))+"/"+outputFolder
        runp = get_infomap_executable_path()
        subprocess.check_call([runp,
                               outputFolder+txt_name,
                               out_path,"-d --directed", "-N 10", "--tree", "-z --zero-based-numbering"])
        subprocess.check_call([runp,
                               outputFolder+txt_name,
                               out_path,"-d --directed", "-N 10", "--bftree", "-z --zero-based-numbering", "--overlapping"])
        # --preferred-number-of-modules 4
        # --overlapping
        with open(outputFolder+txt_name.replace('.net','.tree'), 'rU') as f: # Universal newline mode
            for line in f:
                if line[0] != '#':
                    print line.strip()
                    l = line.strip().split('"')
                    print l
                    modules, flow_amount = l[0].strip().split(" ")
                    node_name = int(l[1])
                    dict_groups[node_name] = float(modules.split(":")[0])

        for n in G.nodes():
            print n, dict_groups.get(n)

    values = [dict_groups.get(node, 0.25) for node in G.nodes()]
    """nx.draw_networkx_edges(G, pos, G.edges())
    nx.draw_networkx_nodes(G,pos,
                           node_color=values,
                           cmap=plt.cm.Set1,
                           node_size=350,
                           alpha=1.0)"""
    nx.draw(G, pos, cmap = plt.get_cmap('jet'), node_color = values)
    nx.draw_networkx_labels(G, pos, font_color='w',  alpha=0.8)
    figManager = plt.get_current_fig_manager()
    if os.name != 'posix':  # mac
        figManager.window.state('zoomed')
    plt.axis('off')
    plt.show()


def draw_step_graph(G, groups, pos=None, louvain=False, step=0, save=False):
    # we need fixed colors, otherwise jumping...
    colors = ['c', 'yellow', 'lightgreen', 'pink', 'red', 'gray', 'b',  'green','darkorange', 'purple', 'maroon']
    #color_dict = {u'Opatija': 'c', u'Zagreb': 'yellow', u'Skocjan': 'lightgreen', u'Trieste':'pink',
    #              u'Bohinj':'red',  u'Ljubljana':'gray', u'Gorje':'b',  u'Bled':'green',
    #              u'Piran/Pirano': 'darkorange', u'Postojna': 'purple'}
    plt.clf()
    if louvain:
        colors = ['c', 'yellow', 'lightgreen', 'pink', 'red', 'gray', 'b',  'green','darkorange', 'purple', 'maroon']
        modularity = Community.modularity(groups, G, 'weight')
        print "Modularity:", modularity
    else:
        map_equation = calculate_map_equation(G, groups)
        print "Map equation", map_equation
    if not pos:
        pos = nx.spring_layout(G)
    nx.draw_networkx_edges(G, pos, G.edges())
    print groups
    #values = [groups.get(node, 0.25) for node in G.nodes()]
    values = [colors[groups.get(node)] for node in G.nodes()]
    #values = [color_dict[groups.get(node)] for node in G.nodes()]
    nx.draw_networkx_nodes(G,pos,
                           node_color=values,
                           node_size=350,
                           alpha=1.0)
    labels = {}
    for n in G.nodes():
        labels[n] = "D"+str(n)
    nx.draw_networkx_labels(G, pos, labels, font_size=8, alpha=0.8)

    from networkx.algorithms import community as community_nx
    #groups = [partition.get(node, 0.25) for node in G.nodes()]
    #modulariry = community_nx.modularity(G, [])
    mng = plt.get_current_fig_manager()
    #if os.name != 'posix':  # mac
    #    figManager.window.state('zoomed')
    plt.axis('off')
    if save:
        if louvain:
            modularity = Community.modularity(groups,G)
            plt.savefig(outputFolder + "/louvain_graph_step="+str(step)+"_modularity_"
                        + str(modularity) + ".png")
        else:
            map_equation = calculate_map_equation(G, groups)
            plt.savefig(outputFolder + "/infomap_graph_step="+str(step)+"_map_equation_"
                        + str(map_equation) + ".png")
    else:
        plt.show()

#draw_louvain(save=False)

import random
from math import log
def calculate_map_equation(G, groups):
    groups_arr =[]
    for k,v in groups.iteritems():
        if v not in groups_arr:
            groups_arr.append(v)
    total_w = 0
    rel_w ={}
    for l in G.edges(data=True):
        total_w += G[l[0]][l[1]]['weight']
    rel_w_sum = 0
    for n in G.nodes():
        rel_w[n] = float(G.degree(n, weight='weight'))/(2 * total_w)
        rel_w_sum += rel_w[n] * log(rel_w[n], 2)

    rel_w_module_i = {}
    rel_w_out_i = {}
    for g in groups_arr:
        rel_w_module_i[g] = 0
        rel_w_out_i[g] = 0
    for l in G.edges(data=True):
        g1 = groups[l[0]]
        g2 = groups[l[1]]
        if g1 != g2:  # link is exiting module
            rel_w_out_i[g1] += float(G[l[0]][l[1]]['weight'])/(2*total_w)
            rel_w_out_i[g2] += float(G[l[0]][l[1]]['weight'])/(2*total_w)
    for n in G.nodes():
        g = groups[n]
        rel_w_module_i[g] += rel_w[n]

    rel_w_out_sum = 0
    total_rel_w_between_modules = 0
    for k,v in rel_w_out_i.iteritems():
        total_rel_w_between_modules += v
        if v == 0:
            rel_w_out_sum += 0
        else:
            rel_w_out_sum += v * log(v,2)

    module_w_sum = 0
    for g in groups_arr:
        module_w_sum += (rel_w_out_i[g]+rel_w_module_i[g]) * log((rel_w_out_i[g]+rel_w_module_i[g]),2)

    if total_rel_w_between_modules==0:
        sum_total_rel_w_between_modules = 0
    else:
        sum_total_rel_w_between_modules = total_rel_w_between_modules * log(total_rel_w_between_modules,2)

    LM = sum_total_rel_w_between_modules - (2 * rel_w_out_sum) - rel_w_sum + module_w_sum
    #print LM
    return LM


def draw_steps(G, louvain=False):  # num_cliques, clique_size)
    #G = nx.ring_of_cliques(num, size)
    #G = nx.balanced_tree(2, 3)

    pos = nx.spring_layout(G)
    dict_groups = {}
    for n in G.nodes():
        dict_groups[n] = n
    if louvain:
        step = 0
        picked_arr = [5, 4, 1, 7, 3, 8, 2, 6, 7, 1, 1]
        draw_step_graph(G, dict_groups, pos, louvain, step,True)
        while True:
            # r = random.randint(0, 8)  this can take a while
            r = picked_arr[step]
            print "Picked: " + str(r)
            modularity = Community.modularity(dict_groups,G)
            b = 0
            group = -1
            for n in sorted(G.neighbors(r)):  # not totally random
                tmp = dict_groups[r]
                dict_groups[r] = n
                tmod = Community.modularity(dict_groups,G)
                print "mod: " + str(tmod) + " for n: "+str(n)
                diff = tmod - modularity
                if b < diff:
                    b = diff
                    group = n
                dict_groups[r] = tmp
            if group != -1:
                dict_groups[r] = group
            step += 1
            draw_step_graph(G, dict_groups, pos, louvain, step, True)
            if step == 10:
                break
        print dict_groups
        # Stage 2: Coarse Graining
        G_coarse = nx.Graph()
        G_coarse.add_edge(1, 2, weight=1)
        G_coarse.add_edge(1, 1, weight=1)
        G_coarse.add_edge(1, 3, weight=1)
        G_coarse.add_edge(2, 3, weight=1)
        G_coarse.add_edge(3, 3, weight=3)
        G_coarse.add_edge(3, 4, weight=2)
        G_coarse.add_edge(4, 4, weight=3)
        dict_c = { 1: 0, 2: 2, 3: 4, 4: 8}
        #for n in G_coarse.nodes():
        #    dict_c[n] = n
        draw_step_graph(G_coarse, dict_c, pos, louvain, True)
        picked_arr = [2, 1]
        step =11
        while True:
            # r = random.randint(0, 8)  this can take a while
            r = picked_arr[step-11]
            print "Picked: " + str(r)
            modularity = Community.modularity(dict_c,G_coarse)
            b = 0
            group = -1
            for n in sorted(G_coarse.neighbors(r)):  # not totally random
                tmp = dict_c[r]
                dict_c[r] = n
                tmod = Community.modularity(dict_c,G_coarse)
                print "mod: " + str(tmod) + " for n: "+str(n)
                diff = tmod - modularity
                if b < diff:
                    b = diff
                    group = n
                dict_c[r] = tmp
            if group != -1:
                dict_c[r] = group
            step += 1
            draw_step_graph(G_coarse, dict_c, pos, louvain, step, True)
            if step == 13:
                break
        final_groups = {0: 2, 1: 2, 2: 2, 3: 4, 4: 4, 5: 4, 6: 8, 7: 8, 8: 8}
        draw_step_graph(G, final_groups, pos, louvain, step+1, True)
    else:
        txt_name = "/infomap_test_steps.net"
        check = False
        if check:
            with open(outputFolder+txt_name, 'w') as f:
                # add nodes and edges to txt and graph
                # A network in Pajek format
                print G.edges()
                newline = str("\n")  # linux
                f.write(str("*Vertices ") + str(len(G.nodes()))+newline)
                c =1
                temp_v = {}
                for n in G.nodes():
                    f.write(str(n)+str(' "'+str(n)+'"'+newline))
                    temp_v[n] = c
                    c += 1  # must follow a consequitive order.
                f.write(str("*Edges ") + str(len(G.edges()))+newline)
                for g in G.edges():
                    f.write(str(str(g[0])+' '+str(g[1]))+newline)
            import os
            out_path = os.path.dirname(os.path.abspath(__file__))+"/"+outputFolder
            runp = get_infomap_executable_path()
            subprocess.check_call([runp,
                                   outputFolder+txt_name,
                                   out_path, "-N 10", "--tree", "-z --zero-based-numbering"])
            # --overlapping
            with open(outputFolder+txt_name.replace('.net','.tree'), 'rU') as f: # Universal newline mode
                for line in f:
                    if line[0] != '#':
                        print line.strip()
                        l = line.strip().split('"')
                        print l
                        modules, flow_amount = l[0].strip().split(" ")
                        node_name = int(l[1])
                        dict_groups[node_name] = int(modules.split(":")[0])

            for n in G.nodes():
                print n, dict_groups.get(n)
            draw_step_graph(G, dict_groups, pos)
            calculate_map_equation(G, dict_groups)

        step = 0
        picked_arr = [1,3, 4, 6, 5, 7, 6, 3, 2, 1]
        draw_step_graph(G, dict_groups, pos, louvain, step, True)
        while True:
            # r = random.randint(0, 8)  this can take a while
            r = picked_arr[step]
            print "Picked: " + str(r)
            map_eq = calculate_map_equation(G, dict_groups)
            #modularity = Community.modularity(dict_groups,G)
            b = 0
            group = -1
            for n in sorted(G.neighbors(r)):  # not totally random
                tmp = dict_groups[r]
                dict_groups[r] = n
                t_map = calculate_map_equation(G, dict_groups)
                print "map eq: " + str(t_map) + " for n: "+str(n)
                diff = map_eq - t_map
                if b < diff:
                    b = diff
                    group = n
                dict_groups[r] = tmp
            if group != -1:
                dict_groups[r] = group
            step += 1
            draw_step_graph(G, dict_groups, pos, louvain, step, True)
            if step == 9:
                break
        print dict_groups
        # Stage 2: Coarse Graining
        print "Coarse"
        G_coarse = nx.Graph()
        G_coarse.add_edge(1, 2, weight=1)
        G_coarse.add_edge(1, 1, weight=1)
        G_coarse.add_edge(1, 3, weight=1)
        G_coarse.add_edge(2, 3, weight=1)
        G_coarse.add_edge(3, 3, weight=3)
        G_coarse.add_edge(3, 4, weight=2)
        G_coarse.add_edge(4, 4, weight=3)
        dict_c = { 1: 0, 2: 2, 3: 5, 4: 8}
        #for n in G_coarse.nodes():
        #    dict_c[n] = n
        draw_step_graph(G, dict_groups, pos, louvain)
        draw_step_graph(G_coarse, dict_c, pos, louvain, step, True)
        picked_arr = [1,4, 2,3]
        step =9
        while True:
            # r = random.randint(0, 8)  this can take a while
            r = picked_arr[step-9]
            print "Picked: " + str(r)
            map_eq = calculate_map_equation(G_coarse, dict_c)
            #modularity = Community.modularity(dict_groups,G)
            b = 0
            group = -1
            for n in sorted(G_coarse.neighbors(r)):  # not totally random
                tmp = dict_c[r]
                dict_c[r] = n
                t_map = calculate_map_equation(G_coarse, dict_c)
                print "map_eq: " + str(t_map) + " for n: "+str(n)
                diff = map_eq - t_map
                if b < diff:
                    b = diff
                    group = n
                dict_c[r] = tmp
            if group != -1:
                dict_c[r] = group
            step += 1
            draw_step_graph(G_coarse, dict_c, pos, louvain, step,True)
            if step == 13:
                break
        final_groups = {0: 2, 1: 2, 2: 2, 3: 2, 4: 2, 5: 2, 6: 8, 7: 8, 8: 8}
        draw_step_graph(G, final_groups, pos, louvain, step+1, True)
        final_groups = {0: 2, 1: 2, 2: 2, 3: 2, 4: 8, 5: 2, 6: 8, 7: 8, 8: 8}
        draw_step_graph(G, final_groups, pos, louvain, step+2, True)
        final_groups = {0: 2, 1: 2, 2: 2, 3: 2, 4: 2, 5: 8, 6: 8, 7: 8, 8: 8}
        draw_step_graph(G, final_groups, pos, louvain, step+2, True)
        # aka by one optim.
        final_groups = {0: 2, 1: 2, 2: 2, 3: 2, 4: 8, 5: 8, 6: 8, 7: 8, 8: 8}
        draw_step_graph(G, final_groups, pos, louvain, step+3, True)
#draw_greedy(5, 4)
#draw_test_di_graph(False)

G = nx.Graph()
for n1,n2 in [(1, 2), (0, 1), (2, 3), (0, 3),
            #  (1, 4),
              (3, 4), (3, 5), (4, 5),
              (4, 6), (5, 6), (6, 7), (6,8), (7, 8)]:
    G.add_edge(n1,n2, weight=1)
"""for n1,n2 in [(0, 1), (1, 2), (2, 3), (0, 3),
              (1, 4),
              (4, 5), (5, 6), (6, 7), (4, 7),
              (2, 8), (7, 8), (8, 9), (2, 9), (7, 9), (8, 9)]:
    G.add_edge(n1,n2)"""
#G = generate_graph()
#min_w = 150# 20#10 ali 20 #372
#G = filter_graph_by_weight(G, min_weight=min_w)
#draw_steps(G, True)


