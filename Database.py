# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from databaseEntities import Base, Record, Pair, Link, Destination, ConnString, folder, DataType, selectedData
from sqlalchemy import create_engine, distinct, func, MetaData, Table, inspect
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
import logging
import datetime as pydatetime
import locale
import itertools

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
    with session_scope() as session:
        session.add_all(records)


def add_row(row_object):
    with session_scope() as session:
        session.add(row_object)


# 2018-02-11 04:14:30.260000 slo ca.4h
def add_records_from_csv(csvreader, n_lines, selectedData):
    records = []
    countErrors =0
    #locale.setlocale(locale.LC_ALL, 'eng_gbr')  # January 15, 2015
    # ValueError:  # not on windows
    with session_scope() as session:
        while not n_lines or csvreader.line_num < n_lines:  # performance?
            row = next(csvreader, None)
            if row is None:
                break
            #print row
            try:
                if selectedData == DataType.SLO:
                    record = Record(csvreader.line_num, row['user_id'].decode('utf-8'),
                                    row['Dodeljena občina'.encode('utf-8')].decode('utf-8'),
                                    pydatetime.datetime.strptime(row['review_date'], '%B %d, %Y'))
                elif selectedData == DataType.LONDON: #decode preveri
                    record = Record(csvreader.line_num, row['user_profile_url'].decode('utf-8'),
                                    row['subject_title'].decode('utf-8'),
                                    pydatetime.datetime.strptime(row['review_date'], '%B %d, %Y'))
                    #record = Record(csvreader.line_num, row['user_username'].decode('utf-8'),
                    #                row['subject_title'].decode('utf-8'),
                    #                pydatetime.datetime.strptime(row['review_date'], '%B %d, %Y'),
                    #                row['user_profile_url'].decode('utf-8'))
                    #                #  ali user_profile_url? najbolje, da kar oboje pobereš
                else: # check problem with whitespaces
                    record = Record(csvreader.line_num, row[' uid'].decode('utf-8').lstrip(),
                                    row['place_name'].decode('utf-8').lstrip(),
                                    pydatetime.datetime.strptime(row[' review_date'].lstrip(), '%Y%M%d'),
                                    row[' username'].decode('utf-8').lstrip())

                if record.user_id:
                    session.add(record)
                    session.flush()
                    #session.commit()
                    records.append(record)
                    # bulk_save_objects
                    # https://stackoverflow.com/questions/4201455/sqlalchemy-whats-the-difference-between-flush-and-commit
            except Exception, ex:
                logging.error(str(countErrors)+". Missing field - error: " + ex.message)
                print row
                #if countErrors > 10:
                #    logging.error("Terminated!")
                #    break
                countErrors += 1
    return records


def add_destinations_from_csv(csvreader, selectedData):
    records = []
    countErrors = 0
    with session_scope() as session:
        while True:
            row = next(csvreader, None)
            if row is None:
                break
            try:
                if selectedData == DataType.SLO:
                    destination = Destination(row['mesto2'].decode('utf-8'),
                                              float(row['Lat'.encode('utf-8')].decode('utf-8').replace(',', '.')),
                                              float(row['Long'.encode('utf-8')].decode('utf-8').replace(',', '.')))
                elif selectedData == DataType.LONDON:
                    lat = float(row['subject_lat'.encode('utf-8')].decode('utf-8').replace('.', ''))
                    if lat < 10:  # errors in data
                        lat *= 10
                    while lat > 500:
                        lat /= 10
                    destination = Destination(row['subject_title'].decode('utf-8'),
                                              lat,
                                              float(row['subject_lng'.encode('utf-8')].decode('utf-8').replace(',', '.')))
                else:
                    destination = Destination(row['place_name'].decode('utf-8').strip(),
                                              float(row[' lat'.encode('utf-8')].decode('utf-8').strip()),
                                              float(row[' lng'.encode('utf-8')].decode('utf-8').strip()))

                if destination.destination:
                    if destination.destination not in records:
                        session.add(destination)
                        records.append(destination.destination)
            except Exception, ex:
                logging.error(str(countErrors)+". Missing field - error: " + ex.message)
                print row
                countErrors += 1
    return records


def delete_records():
    with session_scope() as session:
        session.query(Record).delete()


def delete_pairs():
    with session_scope() as session:
        session.query(Pair).delete()


def delete_links():
    with session_scope() as session:
        session.query(Link).delete()


def delete_destinations():
    with session_scope() as session:
        session.query(Destination).delete()


def delete_all_tables():
    delete_records()
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


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
    return session.query(Link).filter(Link.weight >= weight).order_by(Link.weight.desc()).all()


def fetchall_records_users(session=DBSession(bind=connection)):
    return session.query(distinct(Record.user_id))


def get_destinations(session=DBSession(bind=connection)):
    return session.query(Destination).order_by(Destination.destination.asc())


def get_different_destinations_of_user(user_id):
    session = DBSession(bind=connection)
    return session.query(distinct(Record.destination)).filter(Record.user_id == user_id).order_by(Record.destination.asc())


def get_destinations_of_user(user_id, fid, session=DBSession(bind=connection)):
    return session.query(distinct(Record.destination)).filter(Record.user_id == user_id, Record.flow_id == fid)\
        .order_by(Record.destination.asc()).all()
    #return session.query(Record.user_id, Record.destination).group_by(Record.user_id).all()


def generate_fids(weeks=1):
    with session_scope() as session:
        records = session.query(Record).order_by(Record.user_id, Record.review_date.asc())
        lastRecord = records.first()
        lastRecord.flow_id = 1
        for record in records.all()[0::]:
            if lastRecord.user_id == record.user_id:
                if record.review_date < lastRecord.review_date + pydatetime.timedelta(weeks=weeks):
                    record.flow_id = lastRecord.flow_id
                    #if record.destination == lastRecord.destination:
                    #    lastRecord.delete()
                else:
                    record.flow_id = lastRecord.flow_id + 1
            else:
                record.flow_id = 1
                session.flush()
            lastRecord = record


def reload_data():
    delete_links()
    delete_pairs()
    with session_scope() as session:
        # Order – Item Data (transposed)
        # get all different user_id's with all destinations visited
        all_records_users = fetchall_records_users(session)
        allCount = all_records_users.count() # important
        for count, user_t in enumerate(all_records_users):
            user_id = user_t[0]
            fid = 1
            while True:
                destinations = get_destinations_of_user(user_id, fid, session)
                if not destinations:
                    break
                #for dest in destinations:
                #    print dest
                for pair in list(itertools.combinations(destinations, 2)):
                    # item pair data
                    p = Pair(user_id, pair[0][0], pair[1][0])
                    add_pair_and_update_link(p, session)
                    #add_row(p)
                print "Done Pairs: " + str(float(count)/allCount*100)
                fid += 1


        #for p in fetchall_pairs():
        #    print p

        # co-occurence data
        # generate_links()  # now link is updated when pair is created!


def get_count_for_destinations(destination1, destination2, session=DBSession(bind=connection)):
    return session.query(Pair).filter(Pair.destination1 == destination1, Pair.destination2 == destination2).count()


def add_pair_and_update_link(pair, session):
    session.add(pair)
    link = session.query(Link).filter(Link.destination1 == pair.destination1, Link.destination2 == pair.destination2).first()
    if not link:
        session.add(Link(pair.destination1, pair.destination2, 1))
    else:
        link.weight = link.weight + 1
    session.flush()
    # if you don't include the column and just write m.counter += 1, then the new value would be calculated in
    # Python (and race conditions are likely to happen)
    # statement with += would result in SET counter=4 instead of SET counter=counter+1


def generate_links():
    with session_scope() as session:
        all_destinations = get_destinations(session)
        for count, d1 in enumerate(all_destinations):
            for d2 in all_destinations[::-1]:
                if d1 == d2:
                    break
                link = Link(d1[0], d2[0], get_count_for_destinations(d1[0], d2[0], session))
                #print link
                session.add(link)
            print "Done Links: " + str(float(count)/all_destinations.count()*100)


def get_max_weight():
    session = DBSession(bind=connection)
    return session.query(func.count(Link)).scalar()


def get_max_weight():
    session = DBSession(bind=connection)
    return session.query(func.max(Link.weight)).scalar()


def get_max_link_weight(n=10):
    session = DBSession(bind=connection)
    return session.query(Link).order_by(Link.weight.desc()).limit(n).all()


def get_avg_weight_nonzero():
    session = DBSession(bind=connection)
    return session.query(func.avg(Link.weight)).filter(Link.weight > 0).scalar()
#session.query(MyClass).filter(MyClass.name == 'some name')
#session.query(func.count(distinct(User.name)))
#session.query(func.count(User.name), User.name).group_by(User.name).all()
#[(1, u'ed'), (1, u'fred'), (1, u'mary'), (1, u'wendy')]

