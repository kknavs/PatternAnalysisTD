# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from sqlalchemy import Column, Integer, Float, Unicode, UnicodeText, Float, String, MetaData, Table, DateTime
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import mapper, relationship


Base = declarative_base()


class DataType:
    SLO = 1
    LONDON = 2
    VIENNA = 3
    TEST = 4


selectedData = DataType.TEST


folders = ['161124', '161020', 'vienna', 'test']
folder = 'data/' + folders[selectedData-1]

# postgres
ConnString = 'postgresql+psycopg2://postgres:postgres123@127.0.0.1:5432/PatternAnalysisTD_'+folder.replace('data/', '')
# mac: install postgres - https://gist.github.com/lxneng/741932
# pg_ctl -D /usr/local/var/postgres start
# postgresql+psycopg2://user:password@host:port/dbname[?key=value&key=value...]

# sqlite
#ConnString = 'sqlite:///'+folder+'/PatternAnalysisTD_'+folder.replace('data/', '')+'_2.sqlite'
# https://stackoverflow.com/questionss/2047814/is-it-possible-to-store-python-class-objects-in-sqlite
# http://docs.sqlalchemy.org/en/latest/orm/mapping_styles.html#classical-mappings


class Record(Base):
    __tablename__ = 'record'
    id = Column(Integer, primary_key=True)
    user_id = Column(Unicode)
    # destination_id = Column(Integer, ForeignKey('destination.destination'))
    # destination = relationship("Destination", back_populates="records")
    destination = Column(Unicode)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    user_url = Column(Unicode, nullable=True)
    review_date = Column(DateTime)
    flow_id = Column(Integer, default=0)
    attributes = relationship("Attribute", back_populates="record")

    def __init__(self, record_id, user_id, destination, review_date, user_url=None, latitude=0, longitude=0, flow_id=0):
        self.id = record_id
        self.user_id = user_id
        self.destination = destination
        self.user_url = user_url
        self.latitude = latitude
        self.longitude = longitude
        self.review_date = review_date
        self.flow_id = flow_id

    def __repr__(self):
        return ("<Record(id='%s', user_id='%s', user_url='%s' destination='%s', review_date='%s', flow_id='%s')>" % (
                                 self.id, self.user_id, self.user_url, self.destination,
                                 self.review_date, self.flow_id)).encode('utf-8')


class Attribute(Base):
    __tablename__ = 'attribute'
    id = Column(Integer, primary_key=True, autoincrement=True)
    record_id = Column(Integer, ForeignKey('record.id'))
    record = relationship("Record", back_populates="attributes")
    name = Column(Unicode)
    value = Column(Unicode)

    def __init__(self, record_id, name, value):
        self.record_id = record_id
        self.name = name
        self.value = value

    def __repr__(self):
        return ("<Attribute(id='%s', record_id='%s', user='%s' destination='%s', name='%s', value='%s')>" % (
            self.id, self.record_id, self.record.user_id, self.record.destination,
            self.name, self.value)).encode('utf-8')


class Pair(Base):
    __tablename__ = 'pair'
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


class Destination(Base):  # todokk
    __tablename__ = 'destination'
    id = Column(Integer, primary_key=True)
    destination = Column(UnicodeText)  # better as pk or unique=True?
    latitude = Column(Float)
    longitude = Column(Float)
    # records = relationship("Record", back_populates="destination")

    def __init__(self, destination, latitude, longitude):
        self.destination = destination
        self.latitude = latitude
        self.longitude = longitude

    def __repr__(self):
        return ("<Destination(id='%s',destination1='%s' - lat='%f': long='%f' )>" % (
            self.id, self.destination, self.latitude, self.longitude)).encode('utf-8')


class GeolocationMapping(Base):
    __tablename__ = 'geolocation'
    id = Column(Integer, primary_key=True)
    user_hometown = Column(UnicodeText, unique=True)
    country = Column(UnicodeText, nullable=True)
    formatted_address = Column(UnicodeText, nullable=True)
    lat = Column(Float, nullable=True)
    lng = Column(Float, nullable=True)

    def __init__(self, user_hometown, country=None, formatted_address=None):
        self.user_hometown = user_hometown
        self.country = country
        self.formatted_address = formatted_address

    def __repr__(self):
        return ("<GeolocationMapping(id='%s',user_hometown='%s':country='%s', formatted_address='%s')>" % (
                self.id, self.user_hometown, self.country, self.formatted_address)).encode('utf-8')


# sqlalchemy_example.db file.
#mapper(Record, record)
engine = create_engine(ConnString) #, echo=True)
Base.metadata.create_all(engine)

