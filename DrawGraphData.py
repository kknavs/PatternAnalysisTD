# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import collections
import matplotlib.pyplot as plt
import networkx as nx
from FilterGraph import generate_graph, get_all_available_filters
from DrawGraph import draw_labels, relabel_destination, draw_graph_for_destinations, known_locations_bled, \
    known_locations_ljubljana, change_nodes_position, maxWeight
import pandas as pd
from Database import get_baskets_grouped_by_users_date, get_records_for_user_with_fid,\
    get_count_for_attributte_name_value, get_count_for_attribute_name_value_contains, get_dict_count_for_destinations, \
    get_count_for_attributte_name_value_all, get_destinations, fetchall_records, folder
import numpy as np
import io


def plot_degree_histogram(G, neighbours=False):
    # a bit modified function from:
    # https://networkx.github.io/documentation/stable/auto_examples/drawing/plot_degree_histogram.html#sphx-glr-auto-examples-drawing-plot-degree-histogram-py
    relabel_destination(G)
    if neighbours:
        degree_sequence = sorted([d for n, d in G.degree()], reverse=True)  # degree sequence
        print "Neighbours sequence", degree_sequence
        G_degree = G.degree()
    else:
        degree_sequence = sorted([d for n, d in G.degree(weight='weight')], reverse=True)  # degree sequence
        print "Degree sequence", degree_sequence
        G_degree = G.degree(weight='weight')
    for degree in sorted(list(set(degree_sequence))):
        print degree
        for n, d in G_degree:
            if d == degree:
                print n
                if neighbours:
                    print ', '.join(str(nbr) for nbr in sorted(G.neighbors(n)))
    degreeCount = collections.Counter(degree_sequence)
    deg, cnt = zip(*degreeCount.items())

    fig, ax = plt.subplots()
    plt.bar(deg, cnt, width=0.80, color='b')

    if neighbours:
        plt.title("Histogram stopnje vozlišč")
        plt.xlabel("Stopnja vozlišč")
    else:
        plt.title("Utežene stopnje vozlišč")
        plt.xlabel("Utežena stopnja vozlišč")
    plt.ylabel("Število vozlišč")

    plt.xticks(fontsize=7, rotation=60)
    ax.set_xticks([d + 0.4 for d in deg])
    ax.set_xticklabels(deg)

    # draw graph in inset
    plt.axes([0.4, 0.4, 0.5, 0.5])
    Gcc = sorted(nx.connected_component_subgraphs(G), key=len, reverse=True)[0]
    pos = nx.spring_layout(Gcc)
    plt.axis('off')
    nx.draw_networkx_nodes(Gcc, pos, node_size=20)
    nx.draw_networkx_edges(Gcc, pos, alpha=0.4)
    draw_labels(G, pos, font_size=7)

    print nx.info(G)
    #print nx.info(G, "Ljubljana")  # print degree and neighbours
    plt.show()


def plot_weighted_degree_distribution(G):
    # a bit modified function from:
    # https://networkx.github.io/documentation/stable/auto_examples/drawing/plot_degree_histogram.html#sphx-glr-auto-examples-drawing-plot-degree-histogram-py
    relabel_destination(G)
    degree_sequence = []
    x_labels = []
    x_values = []
    for i, nd in enumerate(sorted(G.degree(weight='weight'))):
        # if i > 150: # Vienna
        n, d = nd
        degree_sequence.append(d)
        x_values.append(i)
        x_labels.append(n)

    fig, ax = plt.subplots()
    x_v_t =x_values
    deg_t = degree_sequence
    plt.bar(x_v_t, deg_t, width=1, color='c', edgecolor="blue", linewidth='0.5')
    for i, v in enumerate(degree_sequence):
        if v > 1000:
            ax.text(i-2.5, v + 50,  str(v), color='blue', fontsize=8)
    plt.title("Utežene stopnje vozlišč")
    plt.xlabel("Destinacije")
    plt.ylabel("Utežena stopnja vozlišča")

    plt.xticks(fontsize=7, rotation=90)
    ax.set_xticks([d for d in x_v_t])
    ax.set_xticklabels(x_labels)

    plt.show()


def print_adjacency_matrix(G, print_latex = False):
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.max_rows', 200)
    relabel_destination(G)
    nodelist = sorted([n for n in G.nodes])
    df = nx.to_pandas_adjacency(G, nodelist=nodelist )
    # Return the graph adjacency matrix as a Pandas DataFrame.
    if print_latex:
        pages = 4
        start = 0
        step = int(len(nodelist)/pages) + (len(nodelist) % pages > 0)
        while True:
            #for nodelist_tmp in [nodelist[start:len(nodelist)/2], nodelist[len(nodelist)/2::]]:
            nodelist_tmp = nodelist[start:start+step]
            """        
            print "lc"* len(nodelist)
            print " & " + ' & '.join(n[0:3] for n in nodelist) + " \\\\ \hline"
            for d in df:
                print d + " & " + ' & '.join(str(n) for n in df[d]) + " \\\\ "
            """
            print "|c" * len(nodelist_tmp)
            print " & " + ' & '.join(n for n in nodelist_tmp) + " \\\\ \hline"
            for d in df:
                print d + " & " + ' & '.join(str(n) for n in df[d][start:start+step]) + " \\\\ "
            start += step
            if start >= len(nodelist):
                break
    else:
        print df


def print_count_for_filters():
    for f in get_all_available_filters():
        print f
        if f.name != 'user_hometown':
            print "Prazne:", get_count_for_attributte_name_value(f.name, '')
            for v in sorted(f.values):
                c = get_count_for_attributte_name_value(f.name, v)
                if f.name == 'user_hometown_country' and c < 1500:
                    continue
                print v, get_count_for_attributte_name_value(f.name, v)
                if 'travel_style' in f.name:
                    print "In: "+v, get_count_for_attribute_name_value_contains(f.name, v)


def draw_histogram_unique_for_user_hometown_country(countries):
    names = []
    cnt = []
    cnt_basic = []
    """for u in fetchall_records_users():
        rec = get_records_for_user_with_fid(u,1)
        if rec:
            r = rec[0]
            print r.attributes"""
    for f in get_all_available_filters():
        if 'user_hometown' in f.name:
            print f.name
            #print "Prazne:", get_count_for_attributte_name_value(f.name, '')
            for v in sorted(countries):
                cc = get_count_for_attributte_name_value_all(f.name, v)
                print len(cc)
                cs = [at.record.user_id for at in cc]
                c = len(set(cs))
                print v, c
                if 'user_hometown_country' in f.name:
                    cnt.append(c)
                    names.append(v)
                else:
                    cnt_basic.append(c)
    fig, ax = plt.subplots()
    plt.bar(names, cnt, width=0.80, color='b')
    plt.bar(names, cnt_basic, width=0.80, color='orange')
    for i, v in enumerate(cnt):
        ax.text(i, v + 50,  str(v), color='b', fontsize=8)
    for i, v in enumerate(cnt_basic):
        ax.text(i-0.4, v + 50,  str(v), color='orange', fontsize=8)
    plt.title("Histogram obiskovalcev po državi uporabnika")
    plt.xlabel("Države")
    plt.ylabel("Število različnih obiskovalcev")

    plt.xticks(fontsize=7, rotation=60)
    ax.set_xticks([i  for i,d in enumerate(names)])
    ax.set_xticklabels(names)
    plt.show()


def draw_histogram_for_user_hometown_country(countries):
    names = []
    cnt = []
    cnt_basic = []
    for f in get_all_available_filters():
        if 'user_hometown' in f.name:
            print f.name
            print "Prazne:", get_count_for_attributte_name_value(f.name, '')
            for v in sorted(countries):
                c = get_count_for_attributte_name_value(f.name, v)
                print v, c
                if 'user_hometown_country' in f.name:
                    cnt.append(c)
                    names.append(v)
                else:
                    cnt_basic.append(c)
    fig, ax = plt.subplots()
    plt.bar(names, cnt, width=0.80, color='b')
    plt.bar(names, cnt_basic, width=0.80, color='orange')
    for i, v in enumerate(cnt):
        ax.text(i, v + 50,  str(v), color='b', fontsize=8)
    for i, v in enumerate(cnt_basic):
        ax.text(i-0.4, v + 50,  str(v), color='orange', fontsize=8)
    plt.title("Histogram zapisov po državi uporabnika")
    plt.xlabel("Države")
    plt.ylabel("Število zapisov")

    plt.xticks(fontsize=7, rotation=60)
    ax.set_xticks([i  for i,d in enumerate(names)])
    ax.set_xticklabels(names)
    plt.show()


def print_baskets_time_info():
    baskets = get_baskets_grouped_by_users_date()
    baskets_dict = dict()
    for b in baskets:
        days = (b[2] - b[3]).days
        if days > 100:  # we do not include it
            print "Days:"+str(days)
            records = get_records_for_user_with_fid(b[0], b[1])
            for r in records:
                print r
        if days not in baskets_dict:
            baskets_dict[days] = 1
        else:
            baskets_dict[days] = baskets_dict[days] + 1
    print "All included:"
    all_c = 0
    sum_avg = 0
    for k in sorted(baskets_dict.keys()):
        print (k+1), baskets_dict[k]
        all_c += baskets_dict[k]
        sum_avg += (k+1)*baskets_dict[k]
    print str( float(sum_avg)/all_c )
    print "Without big:"
    all_c = 0
    sum_avg = 0
    for k in sorted(baskets_dict.keys()):
        if k < 10:
            print k, baskets_dict[k]
            all_c += baskets_dict[k]
            sum_avg += (k+1) * baskets_dict[k]
    print str( float(sum_avg)/all_c )


def draw_all_records():
    destinations = [d.destination for d in get_destinations()]
    known_locations = dict()
    #for d in get_destinations():
    #    known_locations[d.destination] = np.array([d.longitude, d.latitude])
    known_locations["Ljubljanski grad"] = known_locations_ljubljana["Ljubljanski grad"]
    known_locations["Blejsko jezero"] = known_locations_bled["Blejsko jezero"]
    known_locations["Tartinijev trg"] = np.array([13.568644, 45.528600])
    known_locations["Postojnska jama"] = np.array([14.203842, 45.783030])
    known_locations["Trg bana Josipa Jelačića"] = np.array([15.977301, 45.813121])
    draw_graph_for_destinations(destinations, save=False, known_locations=known_locations)


def draw_records_grouped_by_month():
    months_count = []
    for record in fetchall_records():
        months_count.append(record.review_date.month)
    degreeCount = collections.Counter(months_count)
    deg, cnt = zip(*degreeCount.items())

    fig, ax = plt.subplots()
    plt.bar(deg, cnt, width=0.80, color='b')

    plt.title("Frekvenca zapisov po mesecih")
    plt.xlabel("Mesec")
    plt.ylabel("Število zapisov")

    ax.set_xticks([d  for d in deg])
    # ax.set_xticklabels(deg)
    ax.set_xticklabels(["Jan", "Feb", "Mar", "Apr", "Maj", "Jun", "Jul", "Avg", "Sep", "Okt", "Nov", "Dec"])
    plt.show()


def get_n_biggest_values(dictionary, n):
    biggest_entries = sorted(
        dictionary.items(), key=lambda t: t[1], reverse=True)[:n]
    d = [(key, value) for key, value in biggest_entries]
    print d
    return d


def plot_destinations_frequency(from_statistics=False):
    G = nx.Graph()
    dict_count = {}
    for d in get_destinations():
        G.add_node(d.destination)
        dict_count[d.destination]=0
    if from_statistics:
        arrivals = True
        for txt in ["/2018.txt", "/2017.txt"]:
            with io.open(folder+txt, "r", encoding='utf-8') as data:
                loaddata = False
                while True:
                    line = data.readline()
                    if loaddata:
                        arr = line.split("\t")
                        if len(arr) > 0:
                            if arr[0] in G.nodes():
                                if arrivals:
                                    start = 1
                                else:
                                    start = 2
                                for i in range(start, len(arr), 2):
                                    nv = arr[i].strip()
                                    if nv != "z" and nv != "-":
                                        print arr[i]
                                        dict_count[arr[0]] += float(nv)
                    if line.startswith("SLOVENIJA"):
                        loaddata = True
                    if not line:
                        break
        maxw = 0
        for k,v in dict_count.iteritems():
            if v > maxw:
                maxw = v
        nodesize = [1000*dict_count[n]/maxw for n in G.nodes()]
    else:
        dict_count = get_dict_count_for_destinations()
        nodesize = [100*dict_count[n]/maxWeight for n in G.nodes()]
    nodelist = G.nodes()
    pos = nx.spring_layout(G)  # spring, shell, circular positions for all nodes
    change_nodes_position(pos)
    plt.clf()
    if from_statistics:
        node_color = 'orange'
    else:
        node_color = 'c'
    nx.draw_networkx_nodes(G, pos=pos,  node_size=nodesize, nodelist=nodelist, node_color=node_color)
    #draw_labels(G, pos)
    sub_G = nx.Graph()
    if from_statistics:
        nc = 10
    else:
        nc = 20
    for k,v in get_n_biggest_values(dict_count, nc):
        sub_G.add_node(k)
    #change_nodes_position(pos)
    if from_statistics:
        nx.draw_networkx_labels(sub_G, pos, font_size=9, alpha=0.7)
    else:
        draw_labels(sub_G, pos, font_size=9)
    plt.show()


G = generate_graph()

#plot_degree_histogram(G, neighbours=True)
#plot_weighted_degree_distribution(G)
#print_adjacency_matrix(G, True)
#print_baskets_time_info()
#print_count_for_filters()
countries = [
        "Australia",
        "Austria",
        "Belgium",
        "Canada",
        "Croatia",
        "France",
        "Germany",
        "Hungary",
        "Ireland",
        "Israel",
        "Italy",
        "Serbia",
        "Slovenia",
        "Switzerland",
        "The Netherlands",
        "United Kingdom",
        "United States"
]
#draw_histogram_for_user_hometown_country(countries)
#draw_histogram_unique_for_user_hometown_country(countries)
# draw_all_records()
#draw_records_grouped_by_month()
#plot_destinations_frequency()