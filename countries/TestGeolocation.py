# -*- coding: utf-8 -*-
# code from: https://github.com/slawek87/geolocation-python
from geolocation.main import GoogleMaps

if __name__ == "__main__":
    address = "Ljbljana"

    google_maps = GoogleMaps(api_key='AIzaSyCQ1pib8R5zwW6ymQgYo6fDZiep0MctTYY')

    location = google_maps.search(location=address)

    print(location.all())

    my_location = location.first()

    print(my_location.city)
    print(my_location.route)
    print(my_location.street_number)
    print(my_location.postal_code)

    for administrative_area in my_location.administrative_area:
        print("%s: %s" % (administrative_area.area_type, administrative_area.name))

    print(my_location.country)
    print(my_location.country_shortcut)

    print(my_location.formatted_address)

    print(my_location.lat)
    print(my_location.lng)

# AIzaSyCQ1pib8R5zwW6ymQgYo6fDZiep0MctTYY
#https://github.com/googlemaps/google-maps-services-python