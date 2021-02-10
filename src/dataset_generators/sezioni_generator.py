import json
import os
from pymongo import MongoClient

def main():
    client = MongoClient('localhost', 27017)
    db = client['tesi']
    db_sez = db['sezioni']

    dataset_indicatori = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..', 'Datasets/Indicatori/ds385_popolazione_indicatori_popolazione_famiglie_2011_breve-1.json')))
    dataset_censimento = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..', 'Datasets/Censimento_Milano_2011/sezioni_censimento_2011.geojson')))
    fasce = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..', 'Datasets/Indicatori/ds382_popolazione_popolazione_residente_caratteristiche_sezione_censimento_2011c_.json')))
    famiglie = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..', 'Datasets/Indicatori/ds383_popolazione_famiglie_residenti_caratteristiche_sezione_censimento_2011c.json')))

    print("Generating sezioni...")

    #Fasce preprocessing
    fasce_ordered = {}
    for i in fasce:
        obj = {}
        obj["0-5"] = int(i.get("Età < 5 anni"))
        obj["5-9"] = int(i.get("Età 5 - 9 anni"))
        obj["10-14"] = int(i.get("Età 10 - 14 anni"))
        obj["15-19"] = int(i.get("Età 15 - 19 anni"))
        obj["20-24"] = int(i.get("Età 20 - 24 anni"))
        obj["25-29"] = int(i.get("Età 25 - 29 anni"))
        obj["30-34"] = int(i.get("Età 30 - 34 anni"))
        obj["35-39"] = int(i.get("Età 35 - 39 anni"))
        obj["40-44"] = int(i.get("Età 40 - 44 anni"))
        obj["45-49"] = int(i.get("Età 45 - 49 anni"))
        obj["50-54"] = int(i.get("Età 50 - 54 anni"))
        obj["55-59"] = int(i.get("Età 55 - 59 anni"))
        obj["60-64"] = int(i.get("Età 60 - 64 anni"))
        obj["65-69"] = int(i.get("Età 65 - 69 anni"))
        obj["70-74"] = int(i.get("Età 70 - 74 anni"))
        obj["75-100"] = int(i.get("Età > 74 anni"))
        fasce_ordered[i.get("Numero sezione")] = obj

    #Famiglie preprocessing
    famiglie_ordered = {}
    for i in famiglie:
        obj = {}
        obj["tot_famiglie"] = int(i.get("Famiglie residenti"))
        obj["1"] = int(i.get("Famiglie di 1 componente"))
        obj["2"] = int(i.get("Famiglie di 2 componenti"))
        obj["3"] = int(i.get("Famiglie di 3 componenti"))
        obj["4"] = int(i.get("Famiglie di 4 componenti"))
        obj["5"] = int(i.get("Famiglie di 5 componenti"))
        obj["6"] = int(i.get("Famiglie di 6 e oltre componenti"))
        famiglie_ordered[str(i.get("Numero sezione"))] = obj

    indicatori_keys = ["2) Num medio di residenti per edificio ad uso residenziale\u2026",
    "3) Num medio di abitazioni per edificio ad uso residenzial\u2026","4) Num medio di abitazioni occupate da residenti per edifi\u2026",
    "9) Percent di bambini in et\u00e0 prescolare\u2026","14) Percent di abitazioni non occupate\u2026",
    "15) Percent di famiglie monogenitore\u2026","18) Percent di over65 enni che vivono soli\u2026",
    "26) Giovani (0-14) ogni 100 in et\u00e0 attiva (15-64anni) (In\u2026","27) Over65 enni ogni 100 persone in et\u00e0 attiva (15-64 anni)\u2026",
    "28) Percent di popolazione di 15 anni e pi\u00f9 che percepisce\u2026","35) Percent di popolazione residente che si sposta giornal\u2026",
    "40) Numero medio di componenti delle famiglie\u2026"]

    #Ordering Indicatori + fasce
    censimento_cleared = []
    for i in dataset_censimento.get("features"):
        #print(i.get("properties").get("SEZ"))
        legenda = {"legenda":["1) Numero medio di residenti per edificio ad uso residenziale","2) Numero medio di abitazioni per edificio ad uso residenziale",
        "3) Numero medio di abitazioni occupate da residenti per edificio ad uso residenziale","8) Percentuale di bambini in età prescolare","13) Percentuale di abitazioni non occupate",
        "14) Percentuale di famiglie monogenitore","17) Percentuale di 65+ che vivono da soli","25) Giovani (0-14 anni) ogni 100 in età attiva (15-64anni)",
        "26) Over65 enni ogni 100 persone in età attiva (15-64 anni) ","27) Percentuale di popolazione 15+ che percepisce reddito sul totale della popolazione 15+",
        "34) Percentuale di popolazione residente che si sposta giornalmente per studio o lavoro","39) Numero medio di componenti delle famiglie",
        "40) Percentuale di famiglie di un componente"]}
        obj = {}
        for j in dataset_indicatori:
            if (int(j["1) Numero sezione\u2026"]) == i.get("properties").get("SEZ")):
                for key in indicatori_keys:
                    index = str(int(key.split(")",1)[0])-1)
                    if (j.get(key) == None):
                        obj[index] = ""
                    elif (j.get(key) == ""):
                        obj[index] = ""
                    else:
                        obj[index] = float(j.get(key).replace(",","."))
        i["indicatori"] = obj
        i["indicatori"]["fasce"] = fasce_ordered.get(str(i.get("properties").get("SEZ")))   
        i["indicatori"]["famiglie"] =famiglie_ordered.get(str(i.get("properties").get("SEZ"))) 

    #Sort sezioni by properties.SEZ
    sezioni = sorted([int(i.get("properties").get("SEZ")) for i in dataset_censimento.get("features")])
    dataset_cleared = []
    for i in sezioni:
        for j in dataset_censimento.get("features"):
            if (j.get("properties").get("SEZ") == i):
                dataset_cleared.append(j)
    dataset_censimento["features"] = dataset_cleared

    print("Sezioni generated. Dumping to db...")

    with open("Datasets/dataset_completo.geojson", "w") as outfile:
        json.dump(dataset_censimento, outfile, indent=1)

    dataset = json.load(open('Datasets/dataset_completo.geojson'))

    for i in dataset.get("features"):
        db_sez.insert_one(i)

    print("Dumping to db done.")
if __name__ == "__main__":
    main()