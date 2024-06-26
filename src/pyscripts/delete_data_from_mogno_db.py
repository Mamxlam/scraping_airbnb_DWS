from pymongo import MongoClient

def mongo_connect():
    HOST_NAME = 'host'
    PASSWORD = 'pass'
    USERNAME = 'username'
    AUTH_SOURCE = 'auth source'
    PORT = 'port'
    database_name, collect_name = 'eu', 'teamA'
    connection_link = f"mongodb://{USERNAME}:{PASSWORD}@{HOST_NAME}:{PORT}/{AUTH_SOURCE}"
    my_client = MongoClient(connection_link)
    db = my_client[database_name]
    # print(db.list_collection_names())
    team_A_db = db[collect_name]
    return team_A_db

our_db = mongo_connect()
our_db.delete_many({})
# print(len(list(our_db.find())))