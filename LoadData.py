# -*- coding: utf-8 -*-
import csv, json
from Database import *
#from Node import *
import itertools


def read_destinations():
    with open("data/161124/lat_long.csv") as data:
        dialect = csv.Sniffer().sniff(data.read(1024))
        data.seek(0)
        csvreader = csv.DictReader(data, dialect=dialect)
        print("fieldnames: " + str(len(csvreader.fieldnames)) + " " + ",".join(csvreader.fieldnames))
        return csvreader.fieldnames


def read_lines(n_lines):  # for now required fields are user_id, Dodeljena občina
    with open("data/161124/data.csv") as data:
        # line = data.readline().strip()
        # csvreader = csv.reader(data, delimiter=";")
        dialect = csv.Sniffer().sniff(data.read(1024))
        data.seek(0)
        csvreader = csv.DictReader(data, dialect=dialect) # extrasaction - raise ali ignore
        print("fieldnames: " + str(len(csvreader.fieldnames)) + " " + ",".join(csvreader.fieldnames))
        records = []
        while csvreader.line_num < n_lines:
            row = next(csvreader, None)
            if row is None:
                break
            #print ("csvreader: "+str(csvreader.line_num) +'  !! '.join(csvreader.next()))
            print (row['user_id'], row['Dodeljena občina'])
            record = Record(csvreader.line_num, row['user_id'], row['Dodeljena občina'])
            if record.user_id:
                records.append(record)
            # we take line_num as id of record
            #print (row)
            #print(row['user_id'], row['Dodeljena občina'])
            # s = line[i: i+ len(t)]
            # if s == t:
            #     myfile.write(str(i+1)+" ")
        return records


destinations = read_destinations()
reloadData = False
# Filtered Transactional Data
if reloadData:
    records = read_lines(20000)
    delete_all_tables()
    add_records(records)
for user in fetchall_records():
    print user.user_id, user.destination

    # Order – Item Data (transposed)
    # get all different user_id's with all destinations visited
    for user_t in fetchall_records_users():
        user_id = user_t[0]
        destinations = get_destinations_of_user(user_id)
        #for dest in destinations:
        #    print dest
        for pair in list(itertools.combinations(destinations, 2)):
            # item pair data
            p = Pair(user_id, pair[0][0], pair[1][0])
            add_row(p)

    #for p in fetchall_pairs():
    #    print p

    # co-occurence data
    all_destinations = get_destinations()
    for d1 in all_destinations:
        for d2 in all_destinations[::-1]:
            if d1 == d2:
                break
            link = Link(d1[0], d2[0], get_count_for_destinations(d1[0], d2[0]))
            print link
            add_row(link)


for l in fetchall_links():
    print l
testCount = get_count_for_destinations(u"Bled", u"Ljubljana")
print testCount

# https://stackoverflow.com/questions/14509269/best-method-of-saving-data
# http://zetcode.com/db/sqlitepythontutorial/
# https://docs.python.org/2/library/sqlite3.html
#
# https://plot.ly/python/igraph-networkx-comparison/
# https://stackoverflow.com/questions/23235964/interface-between-networkx-and-igraph