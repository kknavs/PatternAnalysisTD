

class Destination:
    """Destination with name, lat and long"""

    def __init__(self, name, latitude, longitude):
        self.name = name
        self.lat = latitude
        self.long = longitude

    def __init__(self, name):
        self.name = name

#
# class Record:
#
#     def __init__(self, record_id, user_id, destination):
#         self.id = record_id
#         self.user_id = user_id
#         self.destination = destination


class Node:

    def __init__(self, node_id, user_id, destination):
        self.id = node_id
        self.user_id = user_id
        self.destination = destination


