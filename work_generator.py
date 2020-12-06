import json
from pymongo import MongoClient
import sys

client = MongoClient('localhost', 27017)
db = client['tesi']
db_famiglie = db['famiglie']
db_sezioni = db['sezioni']
db_lavoro = db['lavoro']

pendolarismo = json.load(open('Datasets/Pendolarismo/ds390_Pendolarismo_entroMI_sezione.json'))
sez_indexes = list(dict.fromkeys([i["Sezione di origine"] for i in pendolarismo]))

pendolarismo_clean = {}
print("Indexing workplaces...")
for i in list(dict.fromkeys([index["Sezione di origine"] for index in pendolarismo])):
    print("Indexing sez:",i)
    pendolarismo_clean[i] = []
    for k in pendolarismo:
        if (i == k["Sezione di origine"]):
            obj = {}
            obj["sez_destinazione"] = k["Sezione di destinazione"]
            obj["motivo"] = k["Motivo"]
            obj["num"] = k["Numerositŕ"]
            pendolarismo_clean[i].append(obj)

pend_sez = []
for i in list(db_sezioni.find()):
    #TODO: CHECK IF NULL
    print(pendolarismo_clean[i["properties"]["SEZ"]])


            




