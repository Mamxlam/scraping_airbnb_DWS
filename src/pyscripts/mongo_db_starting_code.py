# IMPORTS
import pymongo
from pymongo import MongoClient


HOST_NAME = 'GIVEN HOSTNAME '
PASSWORD = 'GIVEN PASSWORD'
USERNAME = 'GIVEN USERNAME'
AUTH_SOURCE ='GIVEN USERNAME'
PORT = 'given port'

connection_link = f"mongodb://{USERNAME}:{PASSWORD}@{HOST_NAME}:{PORT}/{AUTH_SOURCE}"
try:
    my_client = MongoClient(connection_link)
    # print('Online database names')
    # print(my_client.list_database_names())
    #Acess the database
    database_name,collect_name = USERNAME,'teamA'
    first_db = my_client[database_name]
    first_collection = first_db[collect_name]
    # TODO FROM A FILE THAT YOU HAVE AGRRED WITH MARIOS YOU CAN INSERT ALL THE PRODUCED JSON INSIDE THE DATABASE TO
    document_dict = {'an_key4':'an_value4'}
    # Insert many
    document_dictios =[{"Name":"Nikos"},{"Name":"Thomas"},{"Name":"Marios"},{"Name":"Ilias"}]
    result = first_collection.insert_many(document_dictios)
    if result.acknowledged: # True or false if the insertion was succesfull
        print("Document inserted successfully.")
        print("Inserted document ID:", result.inserted_id)
        print(f'We have that results is {result.__dir__()}')
    else:
        raise ValueError("Failed to insert document.")

except Exception as e:
    # Handle connection failure
    raise  ValueError("MongoDB connection failed:", e)

# print('Outside try-except')
# print(f'Mongo db collection we have that {first_db.list_collection_names()}') # TO get all the collection
# print(f'Documents inside Nikos testing {first_collection.find()}')
# for docs in first_collection.find(): # IT IS AN ITERABLE OBJECT SOMEHOW
    # print(docs)
#Erase non necessary docs
