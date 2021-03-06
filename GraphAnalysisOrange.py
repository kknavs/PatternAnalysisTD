# -*- coding: utf-8 -*-
from Database import get_all_baskets, folder, get_destinations
import Orange, os
from DrawGraph import mapping
# pip2 install orange

# https://docs.orange.biolab.si/2/reference/rst/Orange.associate.html


def map_destination(destination):
    if destination in mapping:
        return mapping[destination].decode("utf-8").encode('ascii','ignore')
    return destination


def prepare_input_baskets(output_folder, min_items=2):
    if os.path.isfile(output_folder):
        print "File '" + output_folder + "' already created! Delete it if you want to reload data."
    else:
        get_all_baskets(output_folder, min_items)
    baskets = []
    with open(output_folder, str('r')) as file:
        data = file.readlines()
        for line in data:
            words = line.split(" * ")
            baskets += [words[:-1]]
    return baskets

min_items = 1
output_folder = folder + "/analysis/baskets_min_items_"+str(min_items)+str(".basket")
baskets = prepare_input_baskets(output_folder, min_items)
#data = Orange.data.Table("market-basket.basket")  if file in form
#Bread, Milk
#Bread, Diapers, Beer, Eggs
v = get_destinations().all()
domain = Orange.data.Domain([])
domain.add_metas({Orange.orange.newmetaid(): Orange.feature.Continuous(map_destination(n.destination).decode("utf-8").encode('ascii','ignore'))
                  for n in get_destinations().all()}, True)
# The last argument in add_metas, True, tells that these attributes are "optional".
# Without it, the matrix wouldn't be sparse.

data = Orange.data.Table(domain)

for b in baskets:
    ex = Orange.data.Instance(domain)
    for item in b:
        #print map_destination(item)
        ex[map_destination(item)] = 1
    data.append(ex)

sup = 0.015
conf = 0.1
rules = Orange.associate.AssociationRulesSparseInducer(data, support=sup)
print "%4s %4s  %s" % ("Supp", "Conf", "Rule")
for r in rules: #[:10]:
    print "%4.3f %4.3f %4.3f %4.3f %s" % (r.support, r.confidence, r.lift, r.strength, r)


"""In Apriori, association rule induction is two-stage algorithm first finds itemsets that frequently 
appear in the data and have sufficient support, and then splits them to rules of sufficient confidence.
Function get_itemsets reports on itemsets alone and skips rule induction:"""
#data = Orange.data.Table(output_folder)
ind = Orange.associate.AssociationRulesSparseInducer(support=sup, confidence=conf, storeExamples = True)
# Now itemsets is a list of itemsets along with the examples supporting them since we set store_examples to True.
itemsets = ind.get_itemsets(data)
print "***Itemsets:"+ str(len(itemsets)) + "***"
c = 0
for itemset, tids in itemsets[::-1]: #[:10]:
    if len(itemset) > 1:
        c += 1
        print len(tids)
        # print tids # indexes of itemsets in data, that contains items (not same as in input txt file)
        print "(%4.3f) %s" % (len(tids)/float(len(data)),
                          " ".join(data.domain[item].name for item in itemset))
print c

# heatmap correlation graph
# https://datascience.stackexchange.com/questions/14406/visualizing-items-frequently-purchased-together?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa