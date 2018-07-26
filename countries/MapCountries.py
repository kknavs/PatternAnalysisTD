# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import csv
import logging
from geolocation.main import GoogleMaps
from geolocation import exceptions as exc


def get_set_of_countries_and_code():
    records = set()
    codes = dict()
    count_errors = 0
    # countries-20140629.csv from http://blog.plsoucy.com/2012/04/iso-3166-country-code-list-csv-sql/
    # https://github.com/datasets/country-list/blob/master/data.csv
    with open("countries/countries-20140629.txt") as data:
            dialect = csv.Sniffer().sniff(data.read(1024))
            data.seek(0)
            csvreader = csv.DictReader(data, dialect=dialect)
            while True:
                row = next(csvreader, None)
                if row is None:
                    break
                try:
                    country = row['English Name'].decode('utf-8').title()
                    records.add(country)
                    codes[row['Code'].decode('utf-8').upper()] = country
                except Exception, ex:
                    logging.error(str(count_errors)+". Error: " + ex.message)
                    print row
                    count_errors += 1
    return records, codes


def get_set_of_states():
    records = set()
    # http://iamattila.com/the-dumpster/list-of-50-states-in-text-format-you-can-cut-n-paste.php
    with open("countries/US_states.txt") as data:
        for line in data:
            records.add(line.decode('utf-8').strip())
    return records


def search_address(address):
    google_maps = GoogleMaps(api_key='AIzaSyCQ1pib8R5zwW6ymQgYo6fDZiep0MctTYY')
    try:
        location = google_maps.search(location=address.decode("utf-8"))
        print(location.all())

        my_location = location.first()
        if my_location:
            for administrative_area in my_location.administrative_area:
                print("%s: %s" % (administrative_area.area_type.decode("utf-8"), administrative_area.name.decode("utf-8")))
        else:
            return None, "Empty location", None, None

        print(my_location.country)
        print(my_location.formatted_address)
        print(my_location.lat)
        print(my_location.lng)
        if my_location.country:
            my_location.country = unicode(my_location.country.decode("utf-8"))
        return my_location.country, my_location.formatted_address, \
               my_location.lat, my_location.lng
    except exc.ApiClientException, ex:
        return None, ex.message, None, None
    except UnicodeEncodeError, ex:
        return None, ex.message, None, None
