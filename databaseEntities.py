# -*- coding: utf-8 -*-
from sqlalchemy import Column, Integer, Unicode, UnicodeText, String, MetaData, Table
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import mapper

Base = declarative_base()
ConnString = 'sqlite:///data/PatternAnalysisTD2.sqlite'
# https://stackoverflow.com/questions/2047814/is-it-possible-to-store-python-class-objects-in-sqlite
# http://docs.sqlalchemy.org/en/latest/orm/mapping_styles.html#classical-mappings

# TODO: add destination table


class Record(Base):
    __tablename__ = 'records'
    id = Column(Integer, primary_key=True)
    user_id = Column(String(50))
    destination = Column(UnicodeText)

    def __init__(self, record_id, user_id, destination):
        self.id = record_id
        self.user_id = user_id
        self.destination = unicode(destination)

    def __repr__(self):
        return "<Record(id='%s', user_id='%s', destination='%s')>" % (
                                 self.id, self.user_id, self.destination)


class Pair(Base):
    __tablename__ = 'pairs'
    id = Column(Integer, primary_key=True)
    user_id = Column(String(50))
    destination1 = Column(UnicodeText)
    destination2 = Column(UnicodeText)

    def __init__(self, user_id, destination1, destination2):
        self.user_id = user_id
        self.destination1 = destination1
        self.destination2 = destination2

    def __repr__(self):
        return "<Pair(id='%s', user_id='%s', destination1='%s' - destination2='%s')>" % (
            self.id, self.user_id, self.destination1, self.destination2)


class Link(Base):
    __tablename__ = 'coocurrence_link'
    id = Column(Integer, primary_key=True)
    destination1 = Column(UnicodeText)
    destination2 = Column(UnicodeText)
    weight = Column(Integer)

    def __init__(self, destination1, destination2, weight):
        self.destination1 = destination1
        self.destination2 = destination2
        self.weight = weight

    def __repr__(self):
        return "<Link(id='%s',destination1='%s' - destination2='%s': weight='%s' )>" % (
            self.id, self.destination1, self.destination2, self.weight)

# sqlalchemy_example.db file.
#mapper(Record, record)
engine = create_engine(ConnString) #, echo=True)
Base.metadata.create_all(engine)

