# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from Database import fetchall_links_with_weight_threshold, get_destinations, get_destinations_id_asc, get_max_weight, \
    folder, DataType, selectedData, get_all_different_attributes, get_all_different_values_for_attribute_name,\
    get_records_by_destinations


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


def get_available_filters():
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


def print_available_filters():
    for f in available_filters:
        print f, "Has empty values:", f.has_empty_values()
        print ',\n '.join(f.values)
        print "************************************"


def reset_filters():
    for f in available_filters:
        f.match = []
        f.apply_filter = False


def filter_add_link(link, filters=None):
    t = get_records_by_destinations(link.destination1, link.destination2)
    print link.weight
    print len(t.all())
    reset_filters()
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
    w = len(t.all())
    for tt in t:
        attributes = tt.attributes
        wtmp = w
        for f in available_filters:
            if w < wtmp:
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
        #else:
        #    print tt
        #    print attributes
            #print attributes
    print w
    return w


available_filters = get_available_filters()
print_available_filters()
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

# age: 366, 1-0,  2- 4, 3-25, 4-46, 5-68, 6-38, prazni-185 : links[11]