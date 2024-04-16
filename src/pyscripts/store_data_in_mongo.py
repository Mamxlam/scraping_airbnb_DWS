import pymongo
from pymongo import MongoClient
import sys
#-------------------------------- Credentials ----------------#

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

def store_data_to_mongo(data_list):
    teamaA_collection= mongo_connect()
    teamaA_collection.insert_many(data_list)


