'''

------------------------------------ CAUTION A DOCUMENT SHOULD NOT EXCEDD 16 MB ----------------------------------------

'''
import pymongo
from pymongo import MongoClient
from pprint import pprint
HOST_NAME = 'db.csd.auth.gr'
PASSWORD = 'Gm8WQhwE'
USERNAME = 'eu'
AUTH_SOURCE = 'admin'
PORT = 27117
connection_link_chat_gpt = f"mongodb://{USERNAME}:{PASSWORD}@{HOST_NAME}:{PORT}/{AUTH_SOURCE}"
database_name,collect_name = 'eu','teamA'  # 'Nikos_testing'
connection_link = f"mongodb://{USERNAME}:{PASSWORD}@{HOST_NAME}:{PORT}/{AUTH_SOURCE}"
#Aceess the MONGO DB
my_client = MongoClient(connection_link)
print(my_client.list_database_names())
db = my_client[database_name]
team_a_collection = db[collect_name]
#DELETE/FIND SOME VALUES
result = team_a_collection.find({"$and":[{'Name':'Nikos'},{'Name':"Ilias"}]}) # for both documents
count_res =team_a_collection.count_documents({"$and":[{'Name':'Nikos'},{'Name':"Ilias"}]})
print(count_res)
# for r in result:
#     print(r)

# Θα χρειαστεί κάποια indexing --> μπορείς απλά να κάνεςι pages15+ σελίδες

#TODO 1 DO THE PRE PROCESSING
#TODO PLAY WITH DELETE MANY/DELETE ONE
# See if you can find an esay way for indexing or just dump the data into a datframe and do you job
# TODO ΔΙΑΧΩΡΙΣΜΟΣ ΤΩΝ ΧΑΡΑΚΤΗΡΙΣΤΙΚΩΝ ΩΣΤΕ ΝΑ ΕΙΝΑΙ ΕΤΟΙΜΑ ΓΙΑ ΤΟ ΜΟΝΤΕΛΟ ΜΗΧΑΝΙΚΗΣ ΜΑΘΗΣΗΣ
#check the encode
