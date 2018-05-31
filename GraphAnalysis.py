# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np, sys
from collections import defaultdict
from Database import fetchall_links_with_weight_threshold, get_destinations, get_destinations_id_asc, get_max_weight, \
    folder, DataType, selectedData
from FilterGraph import generate_graph
import pandas as pd
from mlxtend.frequent_patterns import apriori
from mlxtend.frequent_patterns import association_rules
import os

# http://pbpython.com/market-basket-analysis.html
# http://rasbt.github.io/mlxtend/user_guide/frequent_patterns/apriori/

maxWeight = get_max_weight()
multi = maxWeight/1700.0
multi *= 1.1
outputFolder = folder + "/graphs"
links = fetchall_links_with_weight_threshold(1)
destinations_dict = dict()
ids_dict = dict()
for d in get_destinations():
    #print d
    if d.destination not in destinations_dict:
        destinations_dict[d.destination] = d
        ids_dict[d.id] = d.destination
print len(destinations_dict)


def load_networkx_graph(filters=None, min_w=0, max_w=maxWeight+1):
    if filters:
        G = generate_graph(filters)
        for u,v,d in G.edges(data=True):
            if d['weight']>0:
                w = 1
            else:
                w = 0
            d['weight'] = w
    else:
        G = nx.Graph()
        links = fetchall_links_with_weight_threshold(1)
        if min_w < max_w:
            # add nodes and edges
            for l in links:
                if min_w < l.weight < max_w:
                    if l.weight>0:
                        w = 1
                    else:
                        w = 0
                    G.add_edge(l.destination1, l.destination2, weight=w)
    print(nx.info(G))
    return G

""" test:
208
Name:
Type: Graph
Number of nodes: 81
Number of edges: 649
Average degree:  16.0247
"""

def calculate_rules(G, min_support=0.65, confidence=0.8, lift=1.1):
    """Apriori-based frequent substructure mining algorithms share similar characteristics with Apriori based
        frequent itemset mining algorithms. The search for frequent graphs starts with graphs of
        small “size”, and proceeds in a bottom-up manner"""

    # pip2 install MLxtend
    # http://intelligentonlinetools.com/blog/2018/02/10/how-to-create-data-visualization-for-association-rules-in-data-mining/

    pd.set_option('display.max_columns', 500)
    df = nx.to_pandas_adjacency(G)  # Return the graph adjacency matrix as a Pandas DataFrame.
    print df
    # For better readability, we can set use_colnames=True to convert integer values into the respective item names
    frequent_itemsets = apriori(df, min_support=min_support, use_colnames=True)
    frequent_itemsets['length'] = frequent_itemsets['itemsets'].apply(lambda x: len(x))
    #print frequent_itemsets[ (frequent_itemsets['length'] == 3) &
    #                   (frequent_itemsets['support'] >= 0.6) ]
    print frequent_itemsets
    #association_rules(frequent_itemsets, metric="confidence", min_threshold=0.9)
    rules = association_rules(frequent_itemsets, metric="lift", min_threshold=lift)
    rules.head()
    print rules[ (rules['lift'] >= lift) &
           (rules['confidence'] >= confidence)]


    # http://rasbt.github.io/mlxtend/user_guide/frequent_patterns/apriori/
    # http://pbpython.com/market-basket-analysis.html
    # http://intelligentonlinetools.com/blog/2018/02/10/how-to-create-data-visualization-for-association-rules-in-data-mining/
    # https://programminghistorian.org/en/lessons/exploring-and-analyzing-network-data-with-python

filters = {"subject_type": ["attractions"]}
#filters = {"subject_type": ["hotels"]}
filters =  {"subject_type": ["restaurants"]}
filters =  {"gender": ["M"]}
filters = {"user_travel_style": ["60+ Traveler"]}
filters ={"user_travel_style": ["Art and Architecture Lover"]}
#{"user_travel_style": ["Backpacker"]}
G = load_networkx_graph(filters)
calculate_rules(G, min_support=0.4, confidence=0.5, lift=1.1)

# https://networkx.github.io/documentation/stable/reference/readwrite/index.html
# https://algobeans.com/2016/04/01/association-rules-and-the-apriori-algorithm/


# risanje:
# http://intelligentonlinetools.com/blog/2018/02/10/how-to-create-data-visualization-for-association-rules-in-data-mining/

# R
# https://towardsdatascience.com/a-gentle-introduction-on-market-basket-analysis-association-rules-fa4b986a40ce
# https://datascience.stackexchange.com/questions/14406/visualizing-items-frequently-purchased-together?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa