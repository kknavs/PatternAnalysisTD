# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import csv, json
from Database import *
#from Node import *
import itertools
import xlrd, logging

# in excel, save file as Windows comma separated (CSV)


def read_destinations():
    with open("data/161124/lat_long.csv") as data:
        dialect = csv.Sniffer().sniff(data.read(1024))
        data.seek(0)
        csvreader = csv.DictReader(data, dialect=dialect)
        print("fieldnames: " + str(len(csvreader.fieldnames)) + " " + ",".join(csvreader.fieldnames))
        return csvreader.fieldnames


def read_lines(n_lines):  # for now required fields are user_id, Dodeljena občina
    with open("data/161124/data.csv", 'b', encoding='utf8') as data:
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


# pip install xlrd
# https://pypi.python.org/pypi/xlrd#downloads
# http://mattoc.com/read-xlsx-with-xlrd.html
def prepare_csv(filename):
    #path = folder+"/sc_London_161020.xlsx"
    path = folder+"/"+filename
    workbook = xlrd.open_workbook(path, encoding_override="cp1252")  # this can take a while
    worksheet = workbook.sheet_by_index(0)

    # Change this depending on how many header rows are present
    # Set to 0 if you want to include the header data.
    offset = 0

    #  izpustitev stolpcev: https://stackoverflow.com/questions/9917780/python-csv-write-only-certain-fieldnames-not-all
    with open(folder+"/data.csv", 'wb') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=str(';'),
                                quotechar=str('"'), quoting=csv.QUOTE_MINIMAL)
        for i, row in enumerate(range(worksheet.nrows)):
            if i < offset:  # (Optionally) skip headers
                continue
            r = []
            for j, col in enumerate(range(worksheet.ncols)):
                r.append(unicode(worksheet.cell_value(i, j)).encode('utf-8'))
            spamwriter.writerow(r)


def read_lines_london(n_lines=None):  # for now required fields are user_username, subject_title, lat and long
    with open(folder+"/data.csv", "rb") as data:
    #with open(folder+"/ms_sc_London_161020_utf.csv", "rb") as data:
        # line = data.readline().strip()
        dialect = None
        try:
            dialect = csv.Sniffer().sniff(data.read(1024))
        except:
            csvreader = csv.DictReader(data, delimiter=str(';'))
        finally:
            data.seek(0)
            if dialect:
                if dialect.delimiter not in ["\t", ";", ":", ","]:
                    logging.warning('Found delimiter: '+dialect.delimiter)
                    dialect.delimiter = str(";")
                csvreader = csv.DictReader(data, dialect=dialect)  # extrasaction - raise ali ignore
        #if not n_lines:   # performance?
        #    n_lines = sum(1 for row in csvreader)  # row count
        #    data.seek(0)
        #csvreader = csv.DictReader(data, dialect=dialect) # reset count num of csvreader
        #print("fieldnames: " + str(len(csvreader.fieldnames)) + " " + ",".join(csvreader.fieldnames))
        records = add_records_from_csv(csvreader, n_lines, slo)
        return records


# destinations = read_destinations()
reloadData = True
prepareCsv = False
slo = True  # different column fieldnames. TODO: rename
import datetime
print datetime.datetime.now()
# Filtered Transactional Data
if reloadData:
    if prepareCsv:
        prepare_csv('161124_slovenija_v10 harvesine.xlsm')
        exit()
    delete_all_tables()
    records = read_lines_london() #20000
    # add_records(records) we insert all rows at once
for user in fetchall_records():
    print user.user_id, user.destination

if reloadData:
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
            #print link
            add_row(link)


for l in fetchall_links():
    print l
testCount = get_count_for_destinations(u"Bled", u"Ljubljana")
print testCount
print datetime.datetime.now()
# https://stackoverflow.com/questions/14509269/best-method-of-saving-data
# http://zetcode.com/db/sqlitepythontutorial/
# https://docs.python.org/2/library/sqlite3.html
#
# https://plot.ly/python/igraph-networkx-comparison/
# https://stackoverflow.com/questions/23235964/interface-between-networkx-and-igraph