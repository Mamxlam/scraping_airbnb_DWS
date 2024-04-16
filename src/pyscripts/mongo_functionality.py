import pymongo
from pymongo import MongoClient
import sys

def mongo_connect():
    HOST_NAME = 'db.csd.auth.gr'
    PASSWORD = 'Gm8WQhwE'
    USERNAME = 'eu'
    AUTH_SOURCE = 'admin'
    PORT = 27117
    database_name, collect_name = 'eu', 'teamA'
    connection_link = f"mongodb://{USERNAME}:{PASSWORD}@{HOST_NAME}:{PORT}/{AUTH_SOURCE}"
    my_client = MongoClient(connection_link)
    db = my_client[database_name]
    # print(db.list_collection_names())
    team_A_db = db[collect_name]
    return  team_A_db

def filter_region_data(collection_team):
    '''
    Διαλογή (Κάτω απο το κορδελιό) --> 40.6679407859611, 22.88378072171993
    πολυτεχνίου με 26 οκτωβρίου -- > 40.639645929794995, 22.93070276557463
    Πλατεία Ελευθερίας  -->  40.64026965880075, 22.936055566031847
    καλά καθούμενα πολίχνη -->40.658423011999766, 22.942204011116864
    Εσωτερική περιφερειακή (Διασταύρωση με Λαγκαδά) --> 40.67734521453785, 22.938750901961516
    κοντά στα ελληνικά πετρέλαιοα () --> 40.67794183861351, 22.894283931523514
    Μοναστηρίου με εσωτερική περιφερειακή) --> 40.67046831220567, 22.88574478482302
    '''
    wanted_coordinates = \
    [[40.6679407859611, 22.88378072171993],[40.639645929794995, 22.93070276557463],[40.64026965880075, 22.936055566031847],
     [40.658423011999766, 22.942204011116864],[40.67734521453785, 22.938750901961516],
     [40.67794183861351, 22.894283931523514],[40.67046831220567, 22.88574478482302],[40.6679407859611, 22.88378072171993]]
    wanted_region = {"type":"Polygon","coordinates":wanted_coordinates}
    collection_within_polygon = collection_team.find()
    print(len(list(collection_within_polygon)))
    ''''
    we have to update the json fields with type point and must 
    '''
    pass


# ----------------- SOME Mongo Querries ---------------------------------#
teamA_collection = mongo_connect() # Take team's collection
# filter_region_data
# all_json_data_list= list(teamA_collection.find())# Get all documents inside the collection
filter_region_data(teamA_collection)
# print(type(all_json_data_list))
# for al in all_json_data_list:
#     print(al)

