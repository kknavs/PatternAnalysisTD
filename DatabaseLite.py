# -*- coding: utf-8 -*-
import sqlite3 as lite

con = lite.connect('data/PatternAnalysisTD.sqlite')


def check_version():
    with con:
        cur = con.cursor()
        cur.execute('SELECT SQLITE_VERSION()')
        data = cur.fetchone()

        print "SQLite version: %s" % data


def crate_empty_records():
    with con:
        cur = con.cursor()
        cur.execute("DROP TABLE IF EXISTS Records")
        #cur.execute("CREATE TABLE Records(id INT, user_id INT, destination TEXT)")


def insert_into_records(records):
    with con:
        cur = con.cursor()
        cur.executemany("INSERT INTO Records VALUES(?, ?, ?)", records)


def fetchall_records():
    with con:
        cur = con.cursor()
        cur.execute("SELECT * FROM Records")
        rows = cur.fetchall()

        for row in rows:
            print row