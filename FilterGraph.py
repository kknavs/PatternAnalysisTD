# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from Database import fetchall_links_with_weight_threshold, get_destinations, get_destinations_id_asc, get_max_weight, \
    folder, DataType, selectedData, get_all_different_attributes, get_all_different_values_for_attribute_name,\
    get_records_by_destinations_with_location, get_attributte_value_by_name_for_record_id
import networkx as nx
import os, datetime
import numpy as np
from collections import defaultdict
import copy

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
        return ("Filter: name='%s', count_diff_values='%s', apply_filter='%r' match='%s'" % (
            self.name, self.count_diff_values, self.apply_filter, self.match)).encode('utf-8')

    def has_empty_values(self):
        return '' in self.values


class Season:
    ALL = 1
    SUMMER = 2
    WINTER = 3
    NEW_YEAR = 4
    WINTER_WITHOUT_NEW_YEAR = 5


def get_season_string(season):
    if season == Season.ALL:
        return ""
    elif season == Season.SUMMER:
        return "SUMMER"
    elif season == Season.WINTER:
        return "WINTER"
    elif season == Season.WINTER_WITHOUT_NEW_YEAR:
        return "WINTER_WITHOUT_NEW_YEAR"
    elif season == Season.NEW_YEAR:
        return "CHRISTMAS_NEW_YEAR"


def get_season_period(season):
    if season == Season.ALL:
        return [[1, 1], [31, 12]]
    elif season == Season.SUMMER:
        return [[21, 6], [23, 9]]
    elif season == Season.WINTER or season == Season.WINTER_WITHOUT_NEW_YEAR:
        return [[21, 12], [21, 3]]
    elif season == Season.NEW_YEAR:
        return [[25, 12], [2, 1]]


def get_all_available_filters():
    filters = []
    for a in get_all_different_attributes():
        values = get_all_different_values_for_attribute_name(a.name)
        c_values = len(values)
        if len(values) > 10:  # e.g.:  60+ Traveler , Family Vacationer , Art and Architecture Lover ,...
            tmp = []
            for v in values:
                if selectedData == DataType.SLO:
                    splitter = ","
                else:
                    splitter = "&"
                if v[0]:
                    for vt in v[0].split(splitter):
                        if vt.strip() not in tmp:
                            tmp.append(vt.strip())
            values = sorted(tmp)
        else:
            values = [v[0] for v in values]
        if a.name == "user_hometown_country":  # this is not multi attribute, though many values are possible
            c_values = 1
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


def prepare_filters(filters, get_only_active=True):
    if not filters:
        return None
    available_filters = reset_filters()
    f_copies =[]
    if filters:
        keys = filters.keys()[::]
        for f in available_filters:
            if f.name in keys:
                f.apply_filter = True
                f.match = filters[f.name]
                if len(filters[f.name]) > 1:
                    if filters[f.name][1] == ["all"]:  # still needed?
                        f.match = filters[f.name][0]
                        f.text_all = True
                    #else:
                    #    for f_match in filters[f.name]:
                    #        f_copy = copy.deepcopy(f)
                    #        f_copies.append(f_copy)
                    #        f.match = f_match

                keys.remove(f.name)
        if len(keys) > 0:
            print "INVALID FILTERS: "+', '.join(keys)
    if get_only_active:
        return [f for f in available_filters if f.apply_filter]+f_copies
    return available_filters + f_copies


def filter_add_link(link, false_users, filters, season=Season.ALL, check_both_nodes=False, refresh_full_graph_links=False, fname=None):
    """
    Check if link is added based on selected filters. Returns new weight.
    If destination is present, returns dict with record id as key, value is lat & long of records.
    Parameters:
      link - edge_with_weight
      filters - list of Filters, which filters to apply are set with apply_filter attribute (default: None)
    """
    if not filters and season == Season.ALL and not refresh_full_graph_links:
        return link.weight
    season_period = get_season_period(season)
    t = get_records_by_destinations_with_location(link.destination1, link.destination2)
    print "Original weight: "+str(link.weight)

    w = len(t.all())
    print w
    recordsId = dict()
    for tt in t:
        if tt[0].user_id in false_users: #s22:32:50.337475 22:52:53.054646
            w -= 1
            continue
        if season != Season.ALL:
            date1 = tt[3]
            date2 = tt[0].review_date
            if date1 > date2:
                latest = date1
                oldest = date2
            else:
                latest = date2
                oldest = date1
            d_latest = datetime.datetime(latest.year, season_period[1][1], season_period[1][0])
            d_oldest = datetime.datetime(oldest.year, season_period[0][1], season_period[0][0])
            if season == Season.SUMMER:
                if not (latest < d_latest and oldest > d_oldest):
                    w -= 1
                    false_users.add(tt[0].user_id)
                    continue
            else:  # different year in start and end date of season
                if latest.year == oldest.year:
                    if latest > d_latest:
                        d_latest = datetime.datetime(latest.year+1, season_period[1][1], season_period[1][0])
                    else:
                        d_oldest = datetime.datetime(oldest.year-1, season_period[0][1], season_period[0][0])
                if not (latest < d_latest and oldest > d_oldest):
                    w -= 1
                    false_users.add(tt[0].user_id)
                    continue
                else:
                    if season == Season.WINTER_WITHOUT_NEW_YEAR:
                        d_latest = datetime.datetime(d_latest.year, get_season_period(Season.NEW_YEAR)[1][1],
                                                     get_season_period(Season.NEW_YEAR)[1][0])
                        d_oldest = datetime.datetime(d_oldest.year, get_season_period(Season.NEW_YEAR)[0][1],
                                                     get_season_period(Season.NEW_YEAR)[0][0])
                        if latest <= d_latest and oldest >= d_oldest:
                            w -= 1
                            false_users.add(tt[0].user_id)
                            continue

        if not filters:
            if fname:
                fname.write(tt[0].user_id + "**" + str(tt[0].flow_id) + "**" +
                            tt[0].destination + "*" + str(tt[0].id) + "*" +
                            tt[0].review_date.ctime() + "*" + str(tt[0].latitude) + "*" + str(tt[0].longitude) + "**" +
                            tt[1] + "*" + str(tt[2]) + "*" +
                            tt[3].ctime() + "*" + str(tt[5]) + "*" + str(tt[4]) +
                            '\n')
            """if destination:
                if tt[0].destination == destination:
                    recordsId[tt[0].id] = np.array([tt[0].longitude, tt[0].latitude])
                else:
                    recordsId[tt[2]] = np.array([tt[4], tt[5]])"""
            continue
        attributes = tt[0].attributes
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
                                false_users.add(tt[0].user_id)
                                break
                    elif a.name == f.name and not any([a.value == v for v in f.match]):  # or
                        w -= 1
                        false_users.add(tt[0].user_id)
                        break
                    elif a.name == f.name:
                        if check_both_nodes:
                            a_v = get_attributte_value_by_name_for_record_id(f.name, tt[2])[0][0]
                            if not any([a_v == v for v in f.match]):  # or
                                w -= 1
                                false_users.add(tt[0].user_id)
                                break
        else:
            if fname:
                fname.write(tt[0].user_id + "**" + str(tt[0].flow_id) + "**" +
                            tt[0].destination + "*" + str(tt[0].id) + "*" +
                            tt[0].review_date.ctime() + "*" + str(tt[0].latitude) + "*" + str(tt[0].longitude) + "**" +
                            tt[1] + "*" + str(tt[2]) + "*" +
                            tt[3].ctime() + "*" + str(tt[5]) + "*" + str(tt[4]) +
                            '\n')
            """if destination:
                if tt[0].destination == destination:
                    recordsId[tt[0].id] = np.array([tt[0].longitude, tt[0].latitude])
                else:
                    recordsId[tt[2]] = np.array([tt[4], tt[5]])"""
    print "New weight: "+str(w)
    return w


#available_filters = get_all_available_filters()
#print_available_filters(available_filters)

def get_fname(filters=None, season=Season.ALL):
    if not filters:
        f_name = "full"
    else:
        f_name = " ".join("{}_{}".format(k, v).replace("'", "").replace(" ","_") for k, v in filters.items())
    f_name += "_" + get_season_string(season)
    return f_name


def generate_graph(filters=None, refresh=False, season=Season.ALL, refresh_full_graph_links=False, check_both_nodes=False):
    """
    Generate graph, if possible read graph from previously saved file.
    Parameters:
      filters - dict {filter_name :[filter_value ...]}, which filters to apply (default: None)
      refresh - bool, force regenerating graph & refreshing output files (default: False)
    """
    G = nx.Graph()
    f_name = get_fname(filters, season)
    txt_name = "/graph_"+f_name+".net"
    out_path = os.path.dirname(os.path.abspath(__file__))+"/"+outputFolderFilters

    if os.path.exists(out_path+txt_name[:].replace(".net",".edgelist")) and not refresh:
        print "Graph loaded from: "+out_path
        print "Run with refresh=True if you want to regenerate graph!"
        G = nx.read_weighted_edgelist(out_path+txt_name.replace(".net",".edgelist"), delimiter='\t', encoding='utf-8')
        return G
    else:
        print "Generating graph: " + out_path+txt_name + " ..."

    # prepare filters
    filters_to_apply = prepare_filters(filters)
    if selectedData == DataType.VIENNA:
        links = fetchall_links_with_weight_threshold(10)  # considered as not important
    else:
        links = fetchall_links_with_weight_threshold(1)
    # add nodes and edges to txt and graph
    with open(outputFolderFilters+txt_name, 'w') as f, \
            open(outputFolderFilters+txt_name.replace(".net","graph_links.txt"), 'w') as gf:
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
        false_users = set()
        for l in links:
            nw = filter_add_link(l, false_users, filters_to_apply, season=season,
                                 refresh_full_graph_links=refresh_full_graph_links, check_both_nodes=check_both_nodes, fname=gf)
            if nw > 0:
                G.add_edge(l.destination1, l.destination2, weight=nw) # float(nw)/maxW)
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


def filter_graph_by_weight(graph, min_weight, maxWeight=1):
    G = nx.Graph()
    for destination1, destination2, nw in graph.edges(data=True):
        if min_weight <= nw['weight']/float(maxWeight):
            G.add_edge(destination1, destination2, weight=float(nw['weight'])/float(maxWeight))
    return G


def generate_graph_for_destination(destination, filters=None, refresh=False, season=Season.ALL):
    f_name = get_fname(filters, season)
    txt_name = "/graph_"+f_name+"graph_links.txt"
    out_path = os.path.dirname(os.path.abspath(__file__))+"/"+outputFolderFilters

    if os.path.exists(out_path+txt_name) and not refresh:
        print "Graph loaded from: "+out_path
        print "Run with refresh=True if you want to regenerate graph!"
        G = nx.read_weighted_edgelist(out_path+txt_name.replace("graph_links.txt",".edgelist"), delimiter='\t', encoding='utf-8')
    else:
        print "Generating graph: " + out_path+txt_name + " ..."
        G = generate_graph(filters, True, season, refresh_full_graph_links=True)
    if len(G.nodes) == 0:
        print "Empty graph!"
        return
    if destination not in G.nodes():
        return [], {}, []
    print nx.info(G, destination)
    pos = dict()
    pos_count = defaultdict(int)
    G = nx.Graph()
    with open(out_path+txt_name, str('r')) as f:
        for line in f:
            tmp = line.split("**")
            ind = 2
            if len(tmp) == 3:  # if saved without flow_id
                ind = 1
            for i in range(0, 2):
                record_destination, record_id, date, lat, lng = tmp[ind+i].split("*")
                if destination == record_destination:
                    #print record_destination, record_id, date, lat, lng
                    if record_id not in pos:
                        pos_count[lat+lng] += 1
                        pos[record_id] = [lat, lng]
                        G.add_node(record_id)
    nodesize = [pos_count[str(pos[n][0])+str(pos[n][1])] for n in G.nodes]
    # we use string so that there is no float rounding problem
    for k, v in pos.iteritems():
        pos[k] = np.array([float(pos[k][1]), float(pos[k][0])])
    return G.nodes, pos, nodesize


#print nx.info(graph)

""" {"user_travel_style": ["Beach Goer"]},
    {"user_travel_style": ["Eco-tourist"]},
    {"user_travel_style": ["Family Vacationer"]},
    {"user_travel_style": ["Foodie"]}
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
    {"user_travel_style": ["Vegetarian"]}
    """

start = datetime.datetime.now()
filters_arr = [{" age": ["13-17", "18-24"]},
    {" age": ["35-49", "50-64"]},
               {"age": ["65+"]}]
filters_arr =[
    #       {"gender": ["F"]},
    #         {"gender": ["M"]},
    {"age": ["1", "2"]}, {"age": ["3"]},  {"age": ["4", "5"]},  {"age": ["6"]},
    {"user_travel_style": ["Nightlife Seeker"], "age": ["1", "2"]},
    {"user_travel_style": ["Nightlife Seeker"], "age": ["6"]},
]
#for filters in filters_arr:
#    graph = generate_graph(filters=filters, refresh=True)
"""filter = {" travel_style": ["Family Vacationer"]}  # 1: 10, 13  2: 45, 131  1+2: 47, 139
graph = generate_graph(filters=filter, refresh=True)
filter = {" travel_style": ["Nightlife Seeker"]}  # 1: 10, 13  2: 45, 131  1+2: 47, 139
graph = generate_graph(filters=filter, refresh=True)"""
start = datetime.datetime.now()
filter = {" travel_style": ["Backpacker"]}  # 1: 10, 13  2: 45, 131  1+2: 47, 139
filter = {" travel_style": ["Nightlife Seeker"]}
filter = {"user_hometown_country": ["Germany"]}
#graph = generate_graph(filters=filter, refresh=True)
#print nx.info(graph)
print start
print datetime.datetime.now()