# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import csv, json
from Database import *
#from Node import *
import itertools
import xlrd, logging

# in excel, save file as Windows comma separated (CSV)


def read_destinations():
    with open("data/161124/lat_long_transpose_v10.csv") as data:
        dialect = csv.Sniffer().sniff(data.read(1024))
        data.seek(0)
        csvreader = csv.DictReader(data, dialect=dialect)
        dest = add_destinations_from_csv(csvreader, slo)
        return dest


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
prepareCsv = True
reloadRecords = True
reloadFids = True
reloadData = True
reloadDestinations = False

# slo and eng - different column fieldnames. TODO: rename
print pydatetime.datetime.now()

if prepareCsv:
    prepare_csv('161124_slovenija_v10 harvesine.xlsm')
    #exit()

# Filtered Transactional Data
if reloadRecords:
    delete_all_tables()
    records = read_lines_london() #20000
    # add_records(records) we insert all rows at once

if reloadFids:
    generate_fids()

for r in fetchall_records():
    print r

if reloadData:
    delete_links()
    delete_pairs()
    # Order – Item Data (transposed)
    # get all different user_id's with all destinations visited
    all_records_users = fetchall_records_users()
    for count, user_t in enumerate(all_records_users):
        user_id = user_t[0]
        fid = 1
        while True:
            destinations = get_destinations_of_user(user_id, fid)
            if not destinations:
                break
            #for dest in destinations:
            #    print dest
            for pair in list(itertools.combinations(destinations, 2)):
                # item pair data
                p = Pair(user_id, pair[0][0], pair[1][0])
                add_pair_and_update_link(p)
                #add_row(p)
            #print "Done Pairs: " + str(float(count)/all_records_users.count()*100)
            fid += 1

    #for p in fetchall_pairs():
    #    print p

    # co-occurence data
    # generate_links()  # now link is updated when pair is created!


for l in fetchall_links():
    print l
testCount = get_count_for_destinations(u"Bled", u"Ljubljana")
print testCount

if reloadDestinations:
    delete_destinations()
    read_destinations()

    for d in get_destinations():
        print d

print pydatetime.datetime.now()
# https://stackoverflow.com/questions/14509269/best-method-of-saving-data
# http://zetcode.com/db/sqlitepythontutorial/
# https://docs.python.org/2/library/sqlite3.html
#
# https://plot.ly/python/igraph-networkx-comparison/
# https://stackoverflow.com/questions/23235964/interface-between-networkx-and-igraph
