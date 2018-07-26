# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import collections
import matplotlib.pyplot as plt
import networkx as nx
from FilterGraph import generate_graph, get_all_available_filters
from DrawGraph import draw_labels, relabel_destination
import pandas as pd
from Database import get_baskets_grouped_by_users_date, get_records_for_user_with_fid,\
    get_count_for_attributte_name_value, get_count_for_attribute_name_value_contains


def plot_degree_histogram(G, neighbours=False):
    # a bit modified function from:
    # https://networkx.github.io/documentation/stable/auto_examples/drawing/plot_degree_histogram.html#sphx-glr-auto-examples-drawing-plot-degree-histogram-py
    #print nx.adjacency_data(G)
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
    #print nx.adjacency_data(G)
    graph = nx.Graph()
    degree_sequence = []
    x_labels = []
    x_values = []
    for i, nd in enumerate(sorted(G.degree(weight='weight'))):
        n, d = nd
        degree_sequence.append(d)
        x_values.append(i)
        x_labels.append(n)

    fig, ax = plt.subplots()
    x_v_t =x_values
    deg_t = degree_sequence
    plt.bar(x_v_t, deg_t, width=1, color='c', edgecolor="b")
    for i, v in enumerate(degree_sequence):
        if v > 1000:
            ax.text(i-2.5, v - 1.5,  str(v), color='blue', fontsize=8)
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
        pages = 2
        start = 0
        step = len(nodelist)/pages
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
        if 'user_hometown' not in f.name:
            print "Prazne:", get_count_for_attributte_name_value(f.name, '')
            for v in sorted(f.values):
                print v, get_count_for_attributte_name_value(f.name, v)
                if 'travel_style' in f.name:
                    print "In: "+v, get_count_for_attribute_name_value_contains(f.name, v)


def print_baskets_time_info():
    baskets = get_baskets_grouped_by_users_date()
    baskets_dict = dict()
    for b in baskets:
        days = (b[2] - b[3]).days
        if days > 20:  # we do not include it
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
        print k, baskets_dict[k]
        all_c += baskets_dict[k]
        sum_avg += (k+1)*baskets_dict[k]
    print str( float(sum_avg)/all_c )
    """print "Without big:"
    all_c = 0
    sum_avg = 0
    for k in sorted(baskets_dict.keys()):
        if k < 10:
            print k, baskets_dict[k]
            all_c += baskets_dict[k]
            sum_avg += (k+1) * baskets_dict[k]
    print str( float(sum_avg)/all_c )"""


G = generate_graph()

#plot_degree_histogram(G, neighbours=True)
#plot_weighted_degree_distribution(G)
#print_adjacency_matrix(G, True)
#print_baskets_time_info()
print_count_for_filters()