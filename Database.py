# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from databaseEntities import Base, Record, Pair, Link, ConnString, folder
from sqlalchemy import create_engine, distinct, func, MetaData, Table, inspect
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
import logging

engine = create_engine(ConnString) #, echo=True)


# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
connection = engine.connect()
#connection.text_factory = str
#connection.connection.text_factory=str

#metadata = MetaData(engine)
#Records = Table('records', Base.metadata, autoload=True)
# https://stackoverflow.com/questions/2047814/is-it-possible-to-store-python-class-objects-in-sqlite


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = DBSession()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


def add_records(records):
    #for o in records:
    #   Records.insert(o)
    #session.add(o)
    with session_scope() as session:
        session.add_all(records)
        #session.query(Record).add_all(records)
    #connection.execute(Records.insert(), records)


def add_row(row_object):
    with session_scope() as session:
        session.add(row_object)

# 2018-02-11 04:14:30.260000 slo ca.4h
def add_records_from_csv(csvreader, n_lines, slo):
    records = []
    countErrors =0
    with session_scope() as session:
        while not n_lines or csvreader.line_num < n_lines: # performance?
            row = next(csvreader, None)
            if row is None:
                break
            #print row
            #print (row['user_id'], row['Dodeljena občina'])
            try:
                if slo:
                    record = Record(csvreader.line_num, row['user_id'].decode('utf-8'), row['Dodeljena občina'.encode('utf-8')].decode('utf-8'))
                else: #decode preveri
                    record = Record(csvreader.line_num, row['user_username'].decode('utf-8'), row['subject_title'].decode('utf-8'), row['user_profile_url'].decode('utf-8')) # ali user_profile_url? najbolje, da kar oboje pobereš
                if record.user_id:
                    session.add(record)
                    records.append(record)
            except Exception, ex:
                logging.error("Missing field: " + ex.message)
                if countErrors > 10:
                    logging.error("Terminated!")
                    break
                countErrors += 1
    return records


"""def add_records_from_csv(csvreader, n_lines):
    records = []
    with session_scope() as session:
        while not n_lines or csvreader.line_num < n_lines: # performance?
            row = next(csvreader, None)
            if row is None:
                break
            #print row
            #print (row['user_id'], row['Dodeljena občina'])
            record = Record(csvreader.line_num, row['user_username'].decode('utf-8'), row['subject_title'].decode('utf-8'), row['user_profile_url'].decode('utf-8')) # ali user_profile_url? najbolje, da kar oboje pobereš
            if record.user_id:
                session.add(record)
                records.append(record)
    return records"""


def delete_records():
    with session_scope() as session:
        session.query(Record).delete()


def delete_pairs():
    with session_scope() as session:
        session.query(Pair).delete()


def delete_links():
    with session_scope() as session:
        session.query(Link).delete()


def delete_all_tables():
    delete_links()
    delete_pairs()
    delete_records()


def inspect_records():
    with session_scope() as session:
        from sqlalchemy import inspect
        insp = inspect(Record)
        print (list(insp.columns))


def fetchall_records():
    session = DBSession(bind=connection)
    return session.query(Record).all()


def fetchall_pairs():
    session = DBSession(bind=connection)
    return session.query(Pair).all()


def fetchall_links():
    session = DBSession(bind=connection)
    return session.query(Link).all()


def fetchall_links_with_weight_threshold(weight):
    session = DBSession(bind=connection)
    return session.query(Link).filter(Link.weight >= weight)


def fetchall_records_users():
    session = DBSession(bind=connection)
    return session.query(distinct(Record.user_id))


def get_destinations():
    session = DBSession(bind=connection)
    return session.query(distinct(Record.destination)).order_by(Record.destination.asc())


def get_destinations_of_user(user_id):
    session = DBSession(bind=connection)
    return session.query(distinct(Record.destination)).filter(Record.user_id == user_id).order_by(Record.destination.asc())
    #return session.query(Record.user_id, Record.destination).group_by(Record.user_id).all()


def get_count_for_destinations(destination1, destination2):
    session = DBSession(bind=connection)
    return session.query(Pair).filter(Pair.destination1 == destination1, Pair.destination2 == destination2).count()


def get_max_weight():
    session = DBSession(bind=connection)
    return session.query(func.max(Link.weight)).scalar()


def get_avg_weight_nonzero():
    session = DBSession(bind=connection)
    return session.query(func.avg(Link.weight)).filter(Link.weight > 0).scalar()
#session.query(MyClass).filter(MyClass.name == 'some name')
#session.query(func.count(distinct(User.name)))
#session.query(func.count(User.name), User.name).group_by(User.name).all()
#[(1, u'ed'), (1, u'fred'), (1, u'mary'), (1, u'wendy')]

