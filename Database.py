# -*- coding: utf-8 -*-
from databaseEntities import Base, Record, Pair, Link, ConnString
from sqlalchemy import create_engine, distinct, func, MetaData, Table, inspect
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

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

