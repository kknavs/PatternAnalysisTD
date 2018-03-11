# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import csv, json
from Database import *
#from Node import *
import xlrd, logging

# in excel, save file as Windows comma separated (CSV)


def read_destinations():
    if slo:
        with open(folder + "/lat_long_transpose_v11.csv") as data:
            dialect = csv.Sniffer().sniff(data.read(1024))
            data.seek(0)
            csvreader = csv.DictReader(data, dialect=dialect)
            dest = add_destinations_from_csv(csvreader, slo)
            return dest
    else:
        with open(folder+"/data.csv", "rb") as data:
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
def prepare_csv(filename=None):
    if not filename:
        if slo:
            filename = '161124_slovenija_v11 harvesine.xlsm'
        else:
            filename = 'sc_London_161020.xlsx'
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
prepareCsv = False
reloadRecords = False
reloadFids = False
reloadData = False
reloadDestinations = False

# slo and eng - dif
# 2018-02-22 23:45:06.222000
#2018-02-23 01:24:38.106000ferent column fieldnames. TODO: rename

# SAWarning: An exception has occurred during handling of a previous exception.  The previous exception is:
# <class 'sqlalchemy.exc.StatementError'> (exceptions.MemoryError)
# SAWarning: Session's state has been changed on a non-active transaction - this state will be discarded.

if prepareCsv:
    print "***Prepare csv***"
    prepare_csv()
    #exit()

start = pydatetime.datetime.now()
# Filtered Transactional Data
if reloadRecords:
    print "***Reload records***"
    delete_all_tables()
    records = read_lines_london() #20000
    # add_records(records) we insert all rows at once

if reloadFids:
    print "***Reload fids***"
    generate_fids()

#for i,r in enumerate(fetchall_records()):
#    print r
print len(fetchall_records())
print fetchall_records_users().count()  # 2184 empty - only in csv, not in db
"""for user in fetchall_records_users():
    dest = get_different_destinations_of_user(user)
    if dest.count() != 1:
        print user
        print dest.all()"""


if reloadData:
    print "***Reload data***"
    reload_data()
for l in fetchall_links():
    print l

testCount = get_count_for_destinations(u"Bled", u"Ljubljana")
print testCount

if reloadDestinations:
    print "***Reload destinations***"
    delete_destinations()
    read_destinations()

    for d in get_destinations():
        print d

print start
print pydatetime.datetime.now()
# https://stackoverflow.com/questions/14509269/best-method-of-saving-data
# http://zetcode.com/db/sqlitepythontutorial/
# https://docs.python.org/2/library/sqlite3.html
#
# https://plot.ly/python/igraph-networkx-comparison/
# https://stackoverflow.com/questions/23235964/interface-between-networkx-and-igraph
