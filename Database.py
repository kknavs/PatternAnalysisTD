# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from databaseEntities import Base, Record, Attribute, Pair, Link, Destination, ConnString, folder, DataType,\
    selectedData, GeolocationMapping
from sqlalchemy import create_engine, distinct, func, inspect, join, and_
from sqlalchemy.orm import sessionmaker, aliased, joinedload
from contextlib import contextmanager
import logging
import datetime as pydatetime
import locale
import itertools
from countries.MapCountries import *
import time
import io

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
    delete_records()
    delete_attributes()
    records = []
    countErrors =0
    #locale.setlocale(locale.LC_ALL, 'eng_gbr')  # January 15, 2015
    # ValueError:  # if not running on windows
    if selectedData == DataType.SLO:
        # ['user_id', 'Dodeljena občina', 'review_date', 'Lat', 'Long']  too many ignore_columns to write
        attribute_names = ['subject_type', 'user_travel_style', 'user_age', 'gender', 'age', 'user_hometown']
        # cIgnore = 5
    else:
        ignore_columns =[' uid','place_name', ' review_date', ' username', ' lat', ' lng']
        attribute_names = []
        for i,fn in enumerate(csvreader.fieldnames):
            print fn
            if unicode(fn.decode('utf-8')) not in ignore_columns:
                attribute_names.append(fn.decode('utf-8'))
    print attribute_names
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
                                    pydatetime.datetime.strptime(row['review_date'], '%B %d, %Y'), "",
                                    row['subject_lat'].decode('utf-8').strip(),
                                    row['subject_lng'].decode('utf-8').strip())
                elif selectedData == DataType.LONDON:
                    record = Record(csvreader.line_num, row['user_profile_url'].decode('utf-8'),
                                    row['subject_title'].decode('utf-8'),
                                    pydatetime.datetime.strptime(row['review_date'], '%B %d, %Y'))
                    #                row['user_profile_url'].decode('utf-8'))
                    #                #  ali user_profile_url? najbolje, da kar oboje pobereš
                else:  # place_name, place_details, lat, lng, username,
                    # review_date, uid, place_rate, review_rate, travel_style, age, gender
                    record = Record(csvreader.line_num, row[' uid'].decode('utf-8').strip(),
                                    row['place_name'].decode('utf-8').strip(),
                                    pydatetime.datetime.strptime(row[' review_date'].strip(), '%Y%m%d'),
                                    row[' username'].decode('utf-8').strip(),
                                    row[' lat'].decode('utf-8').strip(),
                                    row[' lng'].decode('utf-8').strip())

                if record.user_id:
                    session.add(record)
                    attributes = []
                    for a_n in attribute_names:
                        attribute = Attribute(csvreader.line_num, a_n, row[a_n].decode('utf-8').strip())
                        session.add(attribute)
                    session.flush()
                    #session.commit()  # počasno
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
    # Record.__table__.drop(engine)  # can give error, best to just drop directly!
    with session_scope() as session:
        session.query(Record).delete()


def delete_attributes():
    # Attribute.__table__.drop(engine)
    with session_scope() as session:
        session.query(Attribute).delete()


def delete_pairs():
    with session_scope() as session:
        session.query(Pair).delete()


def delete_links():
    with session_scope() as session:
        session.query(Link).delete()


def delete_destinations():
    with session_scope() as session:
        session.query(Destination).delete()


def delete_geolocation_mappings():
    with session_scope() as session:
        #GeolocationMapping.__table__.drop(engine)
        session.query(GeolocationMapping).delete()


def delete_all_tables():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


def inspect_records():
    with session_scope() as session:
        from sqlalchemy import inspect
        insp = inspect(Record)
        print (list(insp.columns))


def fetchall_records(session=DBSession(bind=connection)):
    return session.query(Record).all()


def fetchall_geolocation_mappings(session=DBSession(bind=connection)):
    return session.query(GeolocationMapping).all()


def fetchall_geolocation_mappings_with_no_country(session=DBSession(bind=connection)):
    return session.query(GeolocationMapping).filter(GeolocationMapping.country=='').all()


def fetchall_pairs():
    session = DBSession(bind=connection)
    return session.query(Pair).all()


def fetchall_links():
    session = DBSession(bind=connection)
    return session.query(Link).all()


def fetchall_links_with_weight_threshold(weight):
    session = DBSession(bind=connection)
    return session.query(Link).filter(Link.weight >= weight).order_by(Link.weight.desc()).all()


def fetchall_links_id_asc_with_weight_threshold(weight):
    session = DBSession(bind=connection)
    return session.query(Link).filter(Link.weight >= weight).order_by(Link.id.asc()).all()


def fetchall_records_users(session=DBSession(bind=connection)):
    #return session.query(Record).distinct(Record.user_id).group_by(Record.user_id)
    return session.query(distinct(Record.user_id))


def get_all_baskets_avg_time_time_spent(output_folder, min_items=2):
    baskets = []
    with session_scope() as session:
        with open(output_folder, str('w')) as file:
            all_records_users = fetchall_records_users(session)
            allCount = all_records_users.count()
            for count, user_t in enumerate(all_records_users):
                user_id = user_t[0]
                fid = 1
                while True:
                    destinations = get_destinations_of_user(user_id, fid, session)
                    if not destinations:
                        break
                    if not len(destinations) < min_items:
                        basket = [d[0] for d in destinations]
                        file.write(' * '.join(basket))  # probably safer not to use comma, can be present in destination
                        baskets.append(basket)
                        file.write(' * '+user_id+str('\n'))
                    fid += 1
                print "Done baskets: " + str(float(count)/allCount*100)
    return baskets


#def  get_users_with_records(session=DBSession(bind=connection)):
#    return session.query(Record).filter(Record.user_id == user_id, Record.flow_id == fid) \
#        .order_by(Record.destination.asc()).all()


def get_records_by_destinations(destination1, destination2, session=DBSession(bind=connection), destination = None):
    if destination:
        return get_records_by_destinations_with_location(destination1, destination2)
    t = session.query(Record.id, Record.user_id, Record.flow_id, Record.destination, Record.review_date).\
        filter(Record.destination==destination1)\
        .group_by(Record.id, Record.user_id,  Record.flow_id, Record.destination).distinct(Record.user_id, Record.flow_id).subquery('t')
    return session.query(Record).filter(and_(
        Record.user_id == t.c.user_id,
        Record.flow_id == t.c.flow_id,
        Record.destination == destination2
        )).distinct(Record.user_id, Record.flow_id).add_column(t.c.destination.label("destination1")) \
        .add_column(t.c.id.label("id1")).add_column(t.c.review_date.label("review_date1"))


def get_records_by_destinations_with_location(destination1, destination2, session=DBSession(bind=connection)):
    t = session.query(Record.id, Record.user_id, Record.flow_id, Record.destination, Record.review_date, Record.latitude,
                      Record.longitude).filter(Record.destination==destination1) \
        .group_by(Record.id, Record.user_id,  Record.flow_id, Record.destination).distinct(Record.user_id, Record.flow_id).subquery('t')
    return session.query(Record).filter(and_(
        Record.user_id == t.c.user_id,
        Record.flow_id == t.c.flow_id,
        Record.destination == destination2
    )).distinct(Record.user_id, Record.flow_id).add_column(t.c.destination.label("destination1")) \
        .add_column(t.c.id.label("id1")).add_column(t.c.review_date.label("review_date1"))\
        .add_column(t.c.longitude.label("lng1")) \
        .add_column(t.c.latitude.label("lat1"))


def get_destinations(session=DBSession(bind=connection)):
    return session.query(Destination).order_by(Destination.destination.asc())


def get_destinations_id_asc(session=DBSession(bind=connection)):
    return session.query(Destination).order_by(Destination.id.asc())


def get_different_destinations_of_user(user_id):
    session = DBSession(bind=connection)
    return session.query(distinct(Record.destination)).filter(Record.user_id == user_id).order_by(Record.destination.asc())


def get_destinations_of_user(user_id, fid, session=DBSession(bind=connection)):
    return session.query(distinct(Record.destination)).filter(Record.user_id == user_id, Record.flow_id == fid)\
        .order_by(Record.destination.asc()).all()
    #return session.query(Record.user_id, Record.destination).group_by(Record.user_id).all()


def get_baskets_grouped_by_users_date(session=DBSession(bind=connection)):
    return session.query(Record.user_id, Record.flow_id, func.max(Record.review_date), func.min(Record.review_date))\
        .order_by(Record.user_id,Record.flow_id).group_by(Record.user_id).group_by(Record.flow_id)


def get_records_for_user_with_fid(user_id, flow_id, session=DBSession(bind=connection)):
    return session.query(Record).filter(and_(Record.user_id == user_id, Record.flow_id == flow_id))\
        .order_by(Record.review_date)


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


def add_geolocation_mapping(user_hometown, country):
    with session_scope() as session:
        mapping = get_geolocation_mapping_by_user_hometown(user_hometown, session)
        if not mapping:
            mapping_new = GeolocationMapping(user_hometown, country)
            session.add(mapping_new)
        else:
            mapping.country = country
        session.commit()


def get_empty_if_none(value):
    if value:
        return value
    return unicode("")


def write_geolocation_mappings():  # then mappings can be transferred to different machine
    with io.open("countries/geolocation_mappings.txt", "w", encoding='utf-8') as data:
        with session_scope() as session:
            for record in fetchall_geolocation_mappings(session):
                data.write(get_empty_if_none(record.user_hometown)+"\t:"+get_empty_if_none(record.country)
                           + "\t:"+get_empty_if_none(record.formatted_address)+"\n")

    print "***Finished writing geolocation_mappings.***"


def read_geolocation_mappings():
    delete_geolocation_mappings()
    with io.open("countries/geolocation_mappings.txt", "r", encoding='utf-8') as data:
        with session_scope() as session:
            while True:
                line = data.readline()
                if not line:
                    break
                user_hometown, country, formatted_address = line.split("\t:")
                print line
                mapping = GeolocationMapping(user_hometown, country, formatted_address.strip())
                session.add(mapping)
                session.flush()

    print "***Finished reading geolocation_mappings.***"


def prepare_geo_location_mappings():
    delete_geolocation_mappings()
    mappings = set()
    with session_scope() as session:
        ctmp =0
        for user_hometown in get_all_different_values_for_attribute_name('user_hometown', session):
                mapping = GeolocationMapping(user_hometown[0], "")
                # tmp = get_geolocation_mapping_by_user_hometown(user_hometown)
                if user_hometown[0] not in mappings:  # sqlalchemy.exc.IntegrityError:
                    mappings.add(user_hometown)
                    print user_hometown
                    session.add(mapping)
                    ctmp += 1
                    if ctmp > 3000:
                        session.commit()
                        ctmp = 0
                    else:
                        session.flush()
    print str(len(mappings))


def generate_geo_location_mappings(insert=True):
    # first try mapping to known countries
    countries, codes = get_set_of_countries_and_code()
    states = get_set_of_states()
    # add special mapping
    add_geolocation_mapping("N.Ireland", "United Kingdom")
    add_geolocation_mapping("Netherlands", "The Netherlands")
    with session_scope() as session:
        print "Locations with no country"
        print str(len(fetchall_geolocation_mappings_with_no_country(session)))
        c = 1000  # request per day https://console.cloud.google.com/iam-admin/quotas?project=analysistd-206520&hl=sl
        ctmp =0
        for loc in fetchall_geolocation_mappings_with_no_country(session):
            if loc.user_hometown is None:
                loc.country = ""
                continue
            if "," in loc.user_hometown:
                loc_items = loc.user_hometown.rsplit(",")
                country = loc_items[-1].strip()
            else:
                country = loc.user_hometown.strip()
                if country in countries:
                    country = country
                elif len(country) > 0:
                    country = country.rsplit()[-1]
                #country = loc.user_hometown.strip()
            country = country.title()
            if country in countries:
                loc.country = country
            elif country in codes:
                loc.country = codes[country]
            elif country in states:
                loc.country = "United States"
            elif "England" in loc.user_hometown.title():
                loc.country = "United Kingdom"
            elif "Deutschland" in loc.user_hometown.title():
                loc.country = "Germany"
            elif c > 0:
                print loc
                a, b, d, e = search_address(loc.user_hometown)
                if a:
                    loc.country = a
                else:
                    loc.formatted_address = b
                #loc.lat = d
                #loc.lng = e
                time.sleep(2)
                c -= 1

            print loc
            ctmp += 1
            if ctmp > 50:  # better to commit frequently
                session.commit()
                ctmp = 0
            else:
                session.flush()
        print "Locations with no country"
        print str(len(fetchall_geolocation_mappings_with_no_country(session)))
        # vsi null po državah: 11451
        # vsi po državah: 5771
        # po US 4135
        # 243
    #return
    with session_scope() as session:
        ctmp =0
        for record in fetchall_records(session):
            user_hometown = get_attributte_value_by_name_for_record_id('user_hometown', record.id, session)[0][0]
            if user_hometown:
                mapping = get_geolocation_mapping_by_user_hometown(user_hometown, session)
                if not mapping:
                    if user_hometown is None:
                        country = ""
                    else:
                        if "," in user_hometown:
                            loc_items = user_hometown.rsplit(",")
                            country = loc_items[-1].strip()
                        else:
                            if user_hometown in countries:
                                country = user_hometown
                            else:
                                country = user_hometown.rsplit()[-1]
                        country = country.title()
                        if country in countries:
                            country = country
                        elif country.upper() in codes:
                            country = codes[country.upper()]
                        elif country in states:
                            country = "United States"
                        elif "England" in user_hometown:
                            country = "United Kingdom"
                        elif "Uk" == user_hometown[-2:].title():
                            country = "United Kingdom"
                        elif "Deutschland" in user_hometown:
                            country = "Germany"
                        else:
                            country = ""
                else:
                    country = mapping.country
            else:
                country = ""

            if not insert:
                a = get_attributte_single_by_name_for_record_id('user_hometown_country', record.id)
                if not a.value and user_hometown:
                #    print country
                #    print user_hometown
                #    print a
                    a.value = country
            else:
                # always new
                attribute = Attribute(record.id, 'user_hometown_country', country)
                session.add(attribute)
            ctmp += 1
            if ctmp > 10000:
                session.commit()
                ctmp = 0
            else:
                session.flush()


#  get_attributte_by_name_for_record_id(name, record_id, session=DBSession(bind=connection))
#        all_records = fetchall_records(session)
#        allCount = all_records.count() # important
def get_count_for_attributte_name_value(name, value,session=DBSession(bind=connection)):
    return session.query(Attribute).filter(and_(Attribute.name == name, Attribute.value == value)).count()


def get_count_for_attributte_name_value_all(name, value, session=DBSession(bind=connection)):
    return session.query(Attribute).join(Record).filter(and_(Attribute.name == name, Attribute.value == value))\
        .distinct(Record.user_id).all()#.count()


def get_count_for_attribute_name_value_contains(name, value,session=DBSession(bind=connection)):
    return session.query(Attribute).filter(and_(Attribute.name == name, Attribute.value.contains(value))).count()


def reload_data():
    delete_links()
    delete_pairs()
    with session_scope() as session:
        # Order – Item Data (transposed)
        # get all different user_id's with all destinations visited
        all_records_users = fetchall_records_users(session)
        allCount = all_records_users.count() # important
        for count, user_t in enumerate(all_records_users):  # todokk: make fids unique?
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

def get_all_baskets(output_folder, min_items=2):
    baskets = []
    with session_scope() as session:
        with open(output_folder, str('w')) as file:
            all_records_users = fetchall_records_users(session)
            allCount = all_records_users.count()
            for count, user_t in enumerate(all_records_users):
                user_id = user_t[0]
                fid = 1
                while True:
                    destinations = get_destinations_of_user(user_id, fid, session)
                    if not destinations:
                        break
                    if not len(destinations) < min_items:
                        basket = [d[0] for d in destinations]
                        file.write(' * '.join(basket))  # probably safer not to use comma, can be present in destination
                        baskets.append(basket)
                        file.write(' * '+user_id+str('\n'))
                    fid += 1
                print "Done baskets: " + str(float(count)/allCount*100)
    return baskets


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
    return session.query(func.max(Link.weight)).scalar()


def get_max_link_weight(n=10):
    session = DBSession(bind=connection)
    return session.query(Link).order_by(Link.weight.desc()).limit(n).all()


def get_avg_weight_nonzero():
    session = DBSession(bind=connection)
    return session.query(func.avg(Link.weight)).filter(Link.weight > 0).scalar()


def get_all_different_attributes(session=DBSession(bind=connection)):
    return session.query(Attribute).distinct(Attribute.name).group_by(Attribute.id) #todokk check why different for sqllite?


def get_all_different_values_for_attribute_name(name, session=DBSession(bind=connection)):
    return session.query(Attribute.value).filter(Attribute.name == name).distinct(Attribute.value).all()


def get_attributte_value_by_name_for_record_id(name, record_id, session=DBSession(bind=connection)):
    return session.query(Attribute.value).filter(Attribute.name == name, Attribute.record_id == record_id)\
        .distinct(Attribute.value).all()


def get_attributte_single_by_name_for_record_id(name, record_id, session=DBSession(bind=connection)):
    return session.query(Attribute).filter(Attribute.name == name, Attribute.record_id == record_id).first()


def get_geolocation_mapping_by_user_hometown(user_hometown, session=DBSession(bind=connection)):
    return session.query(GeolocationMapping).filter(GeolocationMapping.user_hometown==user_hometown).first()
#session.query(MyClass).filter(MyClass.name == 'some name')
#session.query(func.count(distinct(User.name)))
#session.query(func.count(User.name), User.name).group_by(User.name).all()
#[(1, u'ed'), (1, u'fred'), (1, u'mary'), (1, u'wendy')]

