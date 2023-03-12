import pymongo

client = pymongo.MongoClient("mongodb://localhost:27017")

db = client.get_database('AICompany')
col = db['Programmers']

x = col.find()

for i in x:
    print(i)
