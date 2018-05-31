# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from Database import fetchall_links_with_weight_threshold, get_destinations, get_destinations_id_asc, get_max_weight, \
    folder, DataType, selectedData, get_all_different_attributes, get_all_different_values_for_attribute_name,\
    get_records_by_destinations
import networkx as nx
import os

outputFolderFilters = folder + "/filters"


class Filter:
    name = ""
    count_diff_values = 0
    values = []
    apply_filter = False
    match = []
    text_all = False

    def __init__(self, name, count_diff_values, example_values, apply_filter):
        self.name = name
        self.count_diff_values = count_diff_values
        self.values = example_values
        self.apply_filter = apply_filter

    def __repr__(self):
        return ("Filter: name='%s', count_diff_values='%s', apply_filter='%r'" % (
            self.name, self.count_diff_values, self.apply_filter)).encode('utf-8')

    def has_empty_values(self):
        return '' in self.values


def get_all_available_filters():
    filters = []
    for a in get_all_different_attributes():
        values = get_all_different_values_for_attribute_name(a.name)
        c_values = len(values)
        if len(values) > 10:  # e.g.:  60+ Traveler , Family Vacationer , Art and Architecture Lover ,...
            tmp = []
            for v in values:
                for vt in v[0].split(","):
                    if vt.strip() not in tmp:
                        tmp.append(vt.strip())
            values = sorted(tmp)
        else:
            values = [v[0] for v in values]
        filters.append(Filter(a.name, c_values, values, False))
    return filters


def print_available_filters(available_filters):
    for f in available_filters:
        print f, "Has empty values:", f.has_empty_values()
        print ',\n '.join(f.values)
        print "************************************"


def reset_filters():
    available_filters = get_all_available_filters()
    for f in available_filters:
        f.match = []
        f.apply_filter = False
    return available_filters


def prepare_filters(filters):
    if not filters:
        return None
    available_filters = reset_filters()
    if filters:
        keys = filters.keys()[::]
        for f in available_filters:
            if f.name in keys:
                f.apply_filter = True
                f.match = filters[f.name]
                if len(filters[f.name]) > 1:
                    f.match = filters[f.name][0]
                    if filters[f.name][1] == ["all"]:
                        f.text_all = True
                keys.remove(f.name)
        if len(keys) > 0:
            print "INVALID FILTERS: "+', '.join(keys)
    return available_filters


def filter_add_link(link, filters):
    """
    Check if link is added based on selected filters. Returns new weight.
    Parameters:
      link - edge_with_weight
      filters - list of Filters, which filters to apply are set with apply_filter attribute (default: None)
    """
    if not filters:
        return link.weight
    t = get_records_by_destinations(link.destination1, link.destination2)
    print "Original weight: "+str(link.weight)
    print len(t.all())

    w = len(t.all())
    for tt in t:
        attributes = tt.attributes
        wtmp = w
        for f in filters:
            if w < wtmp:  # is enough one filter to fail
                break
            if f.apply_filter:
                for a in attributes:
                    if f.count_diff_values > 10:
                        if a.name == f.name:  # todo: "text-multi"?
                            if (not f.text_all and not any([x.strip() in f.match for x in a.value.split(",")])) :
                                   # or \
                                   # (f.text_all and not all([x.strip() in f.match for x in a.value.split(",")])):  # and
                                w -= 1
                                #print tt
                                #print attributes
                                #print [x.strip() for x in a.value.split(",")]
                                break
                    elif a.name == f.name and not any([a.value == v for v in f.match]):  # or
                        w -= 1
                        break
    print "New weight"+str(w)
    return w


#available_filters = get_all_available_filters()
#print_available_filters()
#links = fetchall_links_with_weight_threshold(1)
#filters = {"age": ["1"]}
#filter_add_link(links[11], filters)
#filters = {"age": ["2"], "user_travel_style":[["Like a Local", "Urban Explorer",""],["all"]]}
#filter_add_link(links[11], filters)
"""filters = {"age": ["3"]}
filter_add_link(links[11], filters)
filters = {"age": ["4"]}
filter_add_link(links[11], filters)
filters = {"age": ["5"]}
filter_add_link(links[11], filters)
filters = {"age": ["6"]}
filter_add_link(links[11], filters)
filters = {"age": [""]}
filter_add_link(links[11], filters)"""


def generate_graph(filters=None, refresh=False):
    """
    Generate graph, if possible read graph from previously saved file.
    Parameters:
      filters - dict {filter_name :[filter_value ...]}, which filters to apply (default: None)
      refresh - bool, force regenerating graph & refreshing output files (default: False)
    """
    G = nx.Graph()
    if not filters:
        f_name = "full"
    else:
        f_name = " ".join("{}_{}".format(k, v).replace("'", "") for k, v in filters.items())
    txt_name = "/graph_"+f_name+".net"
    out_path = os.path.dirname(os.path.abspath(__file__))+"/"+outputFolderFilters

    if os.path.exists(out_path+txt_name[:].replace(".net",".edgelist")) and not refresh:
        print "Graph loaded from: "+out_path
        print "Run with refresh=True if you want to regenerate graph!"
        G = nx.read_weighted_edgelist(out_path+txt_name, delimiter='\t', encoding='utf-8')
        return G
    else:
        print "Generating graph: " + out_path+txt_name + " ..."

    # prepare filters
    filters_to_apply = prepare_filters(filters)
    links = fetchall_links_with_weight_threshold(1)
    # add nodes and edges to txt and graph
    with open(outputFolderFilters+txt_name, 'w') as f:
        # link list format - is a minimal format to describe a network by only specifying a set of links
        # link list has no support for node names, hence we save graph in Pajek format:
        # a network in Pajek format
        """*Vertices 27
        1 "1"
        2 "2"
        3 "3"
        4 "4"
        ...
        *Edges 33
        1 2 1
        1 3 1
        1 4 1
        2 3 1
        ..."""
        for l in links:
            nw = filter_add_link(l, filters_to_apply)
            if nw > 0:
                G.add_edge(l.destination1, l.destination2, weight=nw) #float(nw)/maxW)
        if len(G.nodes()) == 0:
            print "Empty graph!"
            return G
        newline = str("\n")  # linux
        f.write(str("*Vertices ") + str(len(G.nodes()))+newline)
        c = 1
        temp_v = {}
        for d in get_destinations_id_asc():
            if d.destination in G.nodes():
                f.write(str(c)+str(' "'+d.destination+'"'+newline))
                temp_v[d.destination] = c
                c += 1  # must follow a consequitive order.
                #  Labels are quoted directly after the nodes identifier.
        f.write(str("*Edges ") + str(len(G.edges()))+newline)
        for l in G.edges():
            id1 = temp_v[l[0]]
            id2 = temp_v[l[1]]
            e_weight = G[l[0]][l[1]]['weight']
            f.write(str(str(id1)+' '+str(id2)+' '+str(e_weight)+newline))

    nx.write_weighted_edgelist(G, out_path+txt_name[:].replace(".net",".edgelist"), delimiter='\t', encoding='utf-8')
    print "Finished generating, successfully saved."
    return G

# age: 366, 1-0,  2- 4, 3-25, 4-46, 5-68, 6-38, prazni-185 : links[11]

#graph = generate_graph({"age": ["6"]}, refresh=True)
graph = generate_graph({"user_travel_style": ["Backpacker"]}, refresh=True)
#print nx.info(graph)


filters_arr = [
    #{"subject_type": ["attractions"]},
    #          {"subject_type": ["hotels"]},
    #          {"subject_type": ["restaurants"]},
    #          {"gender": ["F"]},
    #          {"gender": ["M"]},
    #          {"age": ["1"]},  {"age": ["2"]},  {"age": ["3"]},
    #          {"age": ["4"]},  {"age": ["5"]},  {"age": ["6"]},
    #          {"user_travel_style": ["60+ Traveler"]},
    {"user_travel_style": ["Art and Architecture Lover"]}]
"""  {"user_travel_style": ["Backpacker"]},
    {"user_travel_style": ["Beach Goer"]},
    {"user_travel_style": ["Eco-tourist"]},
    {"user_travel_style": ["Family Vacationer"]},
    {"user_travel_style": ["Foodie"]},
    {"user_travel_style": ["History Buff"]},
    {"user_travel_style": ["Like a Local"]},
    {"user_travel_style": ["Luxury Traveler"]},
    {"user_travel_style": ["Nature Lover"]},
    {"user_travel_style": ["Nightlife Seeker"]},
    {"user_travel_style": ["Peace and Quiet Seeker"]},
    {"user_travel_style": ["Shopping Fanatic"]},
    {"user_travel_style": ["Thrifty Traveler"]},
    {"user_travel_style": ["Thrill Seeker"]},
    {"user_travel_style": ["Trendsetter"]},
    {"user_travel_style": ["Urban Explorer"]},
    {"user_travel_style": ["Vegetarian"]}]"""
#, "user_travel_style":["Like a Local"]}
"""for filters in filters_arr:
    try:
        generate_graph(filters=filters, save=True)
    except:
        print "Error: "+filters"""
