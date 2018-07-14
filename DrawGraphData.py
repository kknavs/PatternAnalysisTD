# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import collections
import matplotlib.pyplot as plt
import networkx as nx
from FilterGraph import generate_graph
from DrawGraph import draw_labels


def plot_degree_histogram():
    # a bit modified function from:
    # https://networkx.github.io/documentation/stable/auto_examples/drawing/plot_degree_histogram.html#sphx-glr-auto-examples-drawing-plot-degree-histogram-py
    G = generate_graph()

    degree_sequence = sorted([d for n, d in G.degree()], reverse=True)  # degree sequence
    print "Degree sequence", degree_sequence
    for degree in list(set(degree_sequence)):
        print degree
        for n, d in G.degree():
            if d == degree:
                print n
    degreeCount = collections.Counter(degree_sequence)
    deg, cnt = zip(*degreeCount.items())

    fig, ax = plt.subplots()
    plt.bar(deg, cnt, width=0.80, color='b')

    plt.title("Histogram stopnje vozlišč")
    plt.ylabel("Število vozlišč")
    plt.xlabel("Stopnja vozlišč")
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


plot_degree_histogram()