# IMPORTS
import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId

HOST_NAME = 'host'
PASSWORD = 'pass'
USERNAME = 'username'
AUTH_SOURCE ='auth source'
PORT = 'port'




connection_link = f"mongodb://{USERNAME}:{PASSWORD}@{HOST_NAME}:{PORT}/{AUTH_SOURCE}"
try:
    my_client = MongoClient(connection_link)
    # print('Online database names')
    # print(my_client.list_database_names())
    #Acess the database
    database_name,collect_name = USERNAME,'teamA'
    first_db = my_client[database_name] # .get database
    test_name  = 'Nikos_testing'
    first_collection = first_db[collect_name]
    # TODO FROM A FILE THAT YOU HAVE AGRRED WITH MARIOS YOU CAN INSERT ALL THE PRODUCED JSON INSIDE THE DATABASE TO
    # document_dict = {'an_key4':'an_value4'}
    # # Insert many
    document_dictios =[{"Name":"Nikos"},{"Name":"Thomas2"},{"Name":"Marios3"},{"Name":"Ilias4"}] # List of document i want to insert
    # extra_docs = [{"agent":"Bond","sn":0.07,"gun":"AK-47",'mission':'skyfall'}]
    result = first_collection.insert_many(document_dictios)
    # if result.acknowledged: # True or false if the insertion was succesfull
    #     print("Document inserted successfully.")

        # print("Inserted document ID:", result.inserted_id) # A every document has a unique id
        # print(f'We have that results is {result.__dir__()}')
    # else:
    #     raise ValueError("Failed to insert document.")

except Exception as e:
    # Handle connection failure
    raise  ValueError("MongoDB connection failed:", e)

print('Outside try-except')
print(f'Mongo db collection we have that {first_db.list_collection_names()}') # TO get all the collection
# print(f'Documents inside Nikos testing {first_collection.find()}')
# for docs in first_collection.find(): # IT IS AN ITERABLE OBJECT SOMEHOW
#     print(docs)
#Erase non necessary docs


# Make some queries



names = first_collection.find({"Name":'Nikos'}) #find () returns all the results , Curson iter over make it as a list


# Look for a specific field with specific field name
find_nikos = first_collection.find_one({"agent":"Bond"})

#Filtering some elements
filter_nams = first_collection.count_documents(filter={}) # Return nikos  2
# some_counts = first_collection.find().count()


# get something by get_id
_id1 = ObjectId('661432f8cfdf9fec3fb8a44d') # You need this conversion from bson
name_id = first_collection.find_one({'_id':_id1})


# QUERYING IN MONGO DB

# query =  {"$and":[{"Name":'Nikos'},{"Name":'Ilias'}]} # gte greater than equal, lte lower than equal
#
# wanted_name=first_collection.find(query)
# print(list(wanted_name))

# GET SPECIFIC COLUMNS
# projection = {"sn": 0}

# columns ={"_id":0,"gun":1,'mission':1,'agent':1,'sn':0,}
# agentsss= first_collection.find({},columns)
# print(f"my name is {agentsss}")
# for a in agentsss:
    # print(a)

# -delet

# ---------------------------------------------- update or rename
# all_ups = {"$set":{"superhero":True},  # it will overide this field if does exist
           # "$inc":{"age":1},
           # "$rename":{"Name":'nikolakos'}}
# first_collection.update_one({"Name":"Nikos"},all_ups)
# all_remove = {"$unset":{"age":""}}
# first_collection.update_one({"nikolakos":"Nikos"},all_remove)
# print(list(first_collection.find()))


# replace the document with another document --> keept

# new_doc =    {'first_name':'Nikos',"last_name":'Bouzi',"superhero":True}

# first_collection.replace_one({"_id":ObjectId("661432be010827f256a12f6f")},new_doc)

#------------------------------ Deleting elements from the list ---------------------------------------#

first_collection.delete_many({}) # delete oone is also an option
# first_db.drop_collection('Nikos_testing')
# print(f'Mongo db collection we have that {first_db.list_collection_names()}')
