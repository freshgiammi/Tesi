import json
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client['tesi']
db_infanzia = db['scuole_infanzia']
db_elementari = db['scuole_elementari']
db_medie = db['scuole_medie']
db_superiori = db['scuole_superiori']

infanzia = json.load(open('Datasets/Scuole/scuoleinfanzia_2012_2013.geojson'))
elementari = json.load(open('Datasets/Scuole/scuoleprimarie_2012_2013.geojson'))
medie = json.load(open('Datasets/Scuole/scuolesecondarie1grado_2012_2013.geojson'))
superiori = json.load(open('Datasets/Scuole/scuolesecondariesecondogrado.geojson'))

for i in infanzia.get("features"):
    db_infanzia.insert_one(i)
for i in elementari.get("features"):
    db_elementari.insert_one(i)
for i in medie.get("features"):
    db_medie.insert_one(i)
for i in superiori.get("features"):
    db_superiori.insert_one(i)