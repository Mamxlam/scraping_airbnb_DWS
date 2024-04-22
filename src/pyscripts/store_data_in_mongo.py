
#-------------------------------- Credentials ----------------#
import pymongo
from pymongo import MongoClient
import sys
def mongo_connect():
    HOST_NAME = 'USERNAME'
    PASSWORD = 'PASSWORD'
    USERNAME = 'HOST_NAME'
    AUTH_SOURCE = 'AUTH_SOURCE'
    PORT = 'PORT'
    database_name, collect_name = 'database_name', 'collection name'
    connection_link = f"mongodb://{USERNAME}:{PASSWORD}@{HOST_NAME}:{PORT}/{AUTH_SOURCE}"
    my_client = MongoClient(connection_link)
    db = my_client[database_name]
    team_A_db = db[collect_name]
    return  team_A_db

def store_data_to_mongo(data_list):
    teamaA_collection= mongo_connect()
    teamaA_collection.insert_many(data_list)

def delete_mongo_data(given_col):
    erase_collection = given_col.delete_many({})
    return erase_collection


