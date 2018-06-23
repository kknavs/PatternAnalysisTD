# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from Database import fetchall_links_with_weight_threshold, get_destinations, get_destinations_id_asc, get_max_weight, \
    folder, DataType, selectedData, get_all_different_attributes, get_all_different_values_for_attribute_name,\
    get_records_by_destinations, get_attributte_value_by_name_for_record_id
import networkx as nx
import os, datetime
import numpy as np

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


def filter_add_link(link, filters, season=Season.ALL, check_both_nodes=False, destination=None):
    """
    Check if link is added based on selected filters. Returns new weight.
    If destination is present, returns dict with record id as key, value is lat & long of records.
    Parameters:
      link - edge_with_weight
      filters - list of Filters, which filters to apply are set with apply_filter attribute (default: None)
    """
    if not filters and season == Season.ALL and not destination:
        return link.weight
    season_period = get_season_period(season)
    t = get_records_by_destinations(link.destination1, link.destination2, destination=destination)
    print "Original weight: "+str(link.weight)

    w = len(t.all())
    print w
    recordsId = dict()
    for tt in t:
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
                    continue
            else:  # different year in start and end date of season
                if latest.year == oldest.year:
                    if latest > d_latest:
                        d_latest = datetime.datetime(latest.year+1, season_period[1][1], season_period[1][0])
                    else:
                        d_oldest = datetime.datetime(oldest.year-1, season_period[0][1], season_period[0][0])
                if not (latest < d_latest and oldest > d_oldest):
                    w -= 1
                    continue
                else:
                    if season == Season.WINTER_WITHOUT_NEW_YEAR:
                        d_latest = datetime.datetime(d_latest.year, get_season_period(Season.NEW_YEAR)[1][1],
                                                     get_season_period(Season.NEW_YEAR)[1][0])
                        d_oldest = datetime.datetime(d_oldest.year, get_season_period(Season.NEW_YEAR)[0][1],
                                                     get_season_period(Season.NEW_YEAR)[0][0])
                        if latest < d_latest and oldest > d_oldest:
                            w -= 1
                            continue

        if not filters:
            if destination:
                if tt[0].destination == destination:
                    recordsId[tt[0].id] = np.array([tt[0].longitude, tt[0].latitude])
                else:
                    recordsId[tt[2]] = np.array([tt[4], tt[5]])
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
                                break
                    elif a.name == f.name and not any([a.value == v for v in f.match]):  # or
                        w -= 1
                        break
                    elif a.name == f.name:
                        if check_both_nodes:
                            a_v = get_attributte_value_by_name_for_record_id(f.name, tt[2])[0][0]
                            if not any([a_v == v for v in f.match]):  # or
                                w -= 1
                                break
        else:
            if destination:
                if tt[0].destination == destination:
                    recordsId[tt[0].id] = np.array([tt[0].longitude, tt[0].latitude])
                else:
                    recordsId[tt[2]] = np.array([tt[4], tt[5]])
    if destination:
        return recordsId
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


def generate_graph(filters=None, refresh=False, season=Season.ALL, check_both_nodes=False):
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
            if selectedData == DataType.SLO:
                nw = filter_add_link(l, filters_to_apply, season=season, check_both_nodes=check_both_nodes)
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


# TODO:
def generate_graph_for_destination(destination, filters=None, refresh=False, season=Season.ALL):
    """
    Generate graph of records for destination, if possible read graph from previously saved file.
    Parameters:
      filters - dict {filter_name :[filter_value ...]}, which filters to apply (default: None)
      refresh - bool, force regenerating graph & refreshing output files (default: False)
    """
    G = nx.Graph()
    outputFolderFiltersC = outputFolderFilters[::] + "/"+destination
    f_name = get_fname(filters, season)
    txt_name = "/graph_"+f_name+".net"
    out_path = os.path.dirname(os.path.abspath(__file__))+"/"+outputFolderFiltersC

    if os.path.exists(out_path+txt_name[:].replace(".net",".graphML")) and not refresh:
        print "Graph loaded from: "+out_path
        print "Run with refresh=True if you want to regenerate graph!"
        #G = nx.read_graphml(out_path+txt_name.replace(".net",".graphML"))
        return G
    else:
        print "Generating graph: " + out_path+txt_name + " ..."

    # prepare filters
    filters_to_apply = prepare_filters(filters)
    links = fetchall_links_with_weight_threshold(1)
    # add nodes and edges to txt and graph
    pos =dict()
    with open(outputFolderFiltersC+txt_name, 'r') as f:
        for l in links:
            if l.destination1 == destination or l.destination2 == destination:
                nw = filter_add_link(l, filters_to_apply,  destination=destination, season=season)
                if nw:
                    pos.update(nw)
                    for k, v in nw.iteritems():
                        G.add_node(k)
        if len(G.nodes()) == 0:
            print "Empty graph!"
            return G, pos

    outputFolderFiltersC.replace("/"+destination, "")
    #nx.write_graphml(G, out_path+txt_name[:].replace(".net",".graphML"))
    #nx.write_weighted_edgelist(G, out_path+txt_name[:].replace(".net",".edgelist"), delimiter='\t', encoding='utf-8')
    print "Finished generating, successfully saved."
    return G, pos

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
#for filters in filters_arr:
#    generate_graph(filters=filters, refresh=True)