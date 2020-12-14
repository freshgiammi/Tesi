import json
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client['tesi']
db_lavoro = db['lavoro']

pendolarismo = json.load(open('Datasets/Pendolarismo/ds390_Pendolarismo_entroMI_sezione.json'))
sez_indexes = list(dict.fromkeys([i["Sezione di origine"] for i in pendolarismo]))

pendolarismo_clean = {}
print("Indexing workplaces...")
for i in list(dict.fromkeys([index["Sezione di origine"] for index in pendolarismo])):
    print("Indexing sez:",i)
    pendolarismo_clean[i] = []
    for k in pendolarismo:
        if (i == k["Sezione di origine"] and k["Sezione di destinazione"]!="Non determinata" and k["Motivo"]!="Studio"):
            obj = {}
            obj["sez_destinazione"] = k["Sezione di destinazione"]
            obj["motivo"] = k["Motivo"]
            obj["num"] = k["Numerositŕ"]
            pendolarismo_clean[i].append(obj)

for i in pendolarismo_clean:
    db_lavoro.insert_one({"sez":i,"movimenti":pendolarismo_clean[i]})