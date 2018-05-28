# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from Database import get_all_baskets, folder
import Orange, os
# pip2 install orange

# https://docs.orange.biolab.si/2/reference/rst/Orange.associate.html


def prepare_input_baskets(output_folder, min_items=2):
    if os.path.isfile(output_folder):
        print "File '" + output_folder + "' already created! Delete it if you want to reload data."
        baskets = []
        with open(output_folder, str('r')) as file:
            data = file.readlines()
            for line in data:
                words = line.split(",")
                baskets += words
        return baskets
    return get_all_baskets(output_folder, min_items)


output_folder = folder + "/analysis/baskets_min_items_"+str(2)+str(".basket")
baskets = prepare_input_baskets(output_folder)
#data = Orange.data.Table("market-basket.basket")
data = Orange.data.Table(output_folder)

rules = Orange.associate.AssociationRulesSparseInducer(data, support=0.3)
print "%4s %4s  %s" % ("Supp", "Conf", "Rule")
for r in rules[:5]:
    print "%4.1f %4.1f  %s" % (r.support, r.confidence, r)


"""In Apriori, association rule induction is two-stage algorithm first finds itemsets that frequently 
appear in the data and have sufficient support, and then splits them to rules of sufficient confidence.
Function get_itemsets reports on itemsets alone and skips rule induction:"""
data = Orange.data.Table(output_folder)
ind = Orange.associate.AssociationRulesSparseInducer(support=0.2, storeExamples = True)
itemsets = ind.get_itemsets(data)
for itemset, tids in itemsets[:5]:
    print "(%4.2f) %s" % (len(tids)/float(len(data)),
                          " ".join(data.domain[item].name for item in itemset))

# heatmap correlation graph
# https://datascience.stackexchange.com/questions/14406/visualizing-items-frequently-purchased-together?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa