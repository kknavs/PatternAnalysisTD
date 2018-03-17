# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from sqlalchemy import Column, Integer, Unicode, UnicodeText, Float, String, MetaData, Table, DateTime
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import mapper


Base = declarative_base()


class DataType:
    SLO = 1
    LONDON = 2
    VIENNA = 3


selectedData = DataType.VIENNA

#folder = 'data/161020' #London PatternAnalysisTD_161020 17.15  term. 15:02
# 2018-02-24 20:27:01.528000 2018-02-25 22:02:47.971000
# slo: PatternAnalysisTD_161124 from 4.5h to 1h (2018-02-17 12:56:11.098000)
# with add_pair_and_update_link: 2018-02-18 22:37:33.578000 2018-02-18 23:30:09.372000

folders = ['161124', '161020', 'vienna']
folder = 'data/' + folders[selectedData-1]


#ConnString = 'postgresql+psycopg2://postgres:postgres123@127.0.0.1:5432/PatternAnalysisTD_'+folder.replace('data/', '') TODO
#ConnString = 'postgresql+psycopg2://postgres:postgres123@127.0.0.1:5432/PatternAnalysisTD_'+folder.replace('data/', '')+'_fid'
# postgresql+psycopg2://user:password@host:port/dbname[?key=value&key=value...]
# sqlite
ConnString = 'sqlite:///'+folder+'/PatternAnalysisTD_'+folder.replace('data/', '')+'.sqlite'
# https://stackoverflow.com/questionss/2047814/is-it-possible-to-store-python-class-objects-in-sqlite
# http://docs.sqlalchemy.org/en/latest/orm/mapping_styles.html#classical-mappings


class Record(Base):
    __tablename__ = 'records'
    id = Column(Integer, primary_key=True)
    user_id = Column(Unicode)
    destination = Column(Unicode)
    user_url = Column(Unicode, nullable=True)
    review_date = Column(DateTime)
    flow_id = Column(Integer, default=0)  # todokk preveri unicode

    def __init__(self, record_id, user_id, destination, review_date, user_url=None, flow_id=0):
        self.id = record_id
        self.user_id = user_id
        self.destination = destination
        self.user_url = user_url
        self.review_date = review_date
        self.flow_id = flow_id

    def __repr__(self):
        return ("<Record(id='%s', user_id='%s', user_url='%s' destination='%s', review_date='%s', flow_id='%s')>" % (
                                 self.id, self.user_id, self.user_url, self.destination,
                                 self.review_date, self.flow_id)).encode('utf-8')


class Pair(Base):
    __tablename__ = 'pairs'
    id = Column(Integer, primary_key=True)
    user_id = Column(UnicodeText)
    destination1 = Column(UnicodeText)
    destination2 = Column(UnicodeText)

    def __init__(self, user_id, destination1, destination2):
        self.user_id = unicode(user_id)
        self.destination1 = unicode(destination1)
        self.destination2 = unicode(destination2)

    def __repr__(self):
        return ("<Pair(id='%s', user_id='%s', destination1='%s' - destination2='%s')>" % (
            self.id, self.user_id, self.destination1, self.destination2)).encode('utf-8')


class Link(Base):
    __tablename__ = 'coocurrence_link'
    id = Column(Integer, primary_key=True)
    destination1 = Column(UnicodeText)
    destination2 = Column(UnicodeText)
    weight = Column(Integer, default=0)

    def __init__(self, destination1, destination2, weight):
        self.destination1 = destination1
        self.destination2 = destination2
        self.weight = weight

    def __repr__(self):
        return ("<Link(id='%s',destination1='%s' - destination2='%s': weight='%s' )>" % (
            self.id, self.destination1, self.destination2, self.weight)).encode('utf-8')


class Destination(Base): # todokk
    __tablename__ = 'destinations'
    id = Column(Integer, primary_key=True)
    destination = Column(UnicodeText)
    latitude = Column(Float)
    longitude = Column(Float)

    def __init__(self, destination, latitude, longitude):
        self.destination = destination
        self.latitude = latitude
        self.longitude = longitude

    def __repr__(self):
        return ("<Destination(id='%s',destination1='%s' - lat='%f': long='%f' )>" % (
            self.id, self.destination, self.latitude, self.longitude)).encode('utf-8')

# sqlalchemy_example.db file.
#mapper(Record, record)
engine = create_engine(ConnString) #, echo=True)
Base.metadata.create_all(engine)

