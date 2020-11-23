import json
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client['tesi']
db_sez = db['sezioni']

dataset = json.load(open('Datasets/dataset_completo.geojson'))

for i in dataset.get("features"):
    db_sez.insert_one(i)
