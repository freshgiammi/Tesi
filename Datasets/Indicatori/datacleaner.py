import json

dataset_indicatori = json.load(open("Datasets/Indicatori/ds385_popolazione_indicatori_popolazione_famiglie_2011_breve-1.json"))
dataset_censimento = json.load(open("Datasets/Censimento_Milano_2011/sezioni_censimento_2011.geojson"))
fasce = json.load(open("Datasets/Indicatori/ds382_popolazione_popolazione_residente_caratteristiche_sezione_censimento_2011c_.json"))
famiglie = json.load(open("Datasets/Indicatori/ds383_popolazione_famiglie_residenti_caratteristiche_sezione_censimento_2011c.json"))

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

#Ordering Indicatori + fasce
list = []
for i in dataset_indicatori:
    obj = {}
    for j in i:
        index = str(j.split(")",1)[0])
        if (index == "2" or index == "3" or index == "4" or index == "9" or index == "14" or index == "15" or index == "18" or index == "26" or  index == "27" or index == "28" or index == "35" or index == "40" or index == "41"):
            if (i.get(j) == None):
                obj[index] = ""
            elif (i.get(j) == ""):
                obj[index] = ""
            else:
                obj[index] = float(i.get(j).replace(",","."))
        elif (index == "1"):
            obj["sez"] = int(i.get(j))
        else:
            continue
    obj["fasce"] = fasce_ordered.get(str(obj["sez"]))   
    obj["famiglie"] =famiglie_ordered.get(str(obj["sez"])) 
    list.append(obj)

#Data sorting and Indicatori + fasce generation code
indicatori = {"legenda":["1) Numero medio di residenti per edificio ad uso residenziale","2) Numero medio di abitazioni per edificio ad uso residenziale",
"3) Numero medio di abitazioni occupate da residenti per edificio ad uso residenziale","8) Percentuale di bambini in età prescolare","13) Percentuale di abitazioni non occupate",
"14) Percentuale di famiglie monogenitore","17) Percentuale di 65+ che vivono da soli","25) Giovani (0-14 anni) ogni 100 in età attiva (15-64anni)",
"26) Over65 enni ogni 100 persone in età attiva (15-64 anni) ","27) Percentuale di popolazione 15+ che percepisce reddito sul totale della popolazione 15+",
"34) Percentuale di popolazione residente che si sposta giornalmente per studio o lavoro","39) Numero medio di componenti delle famiglie",
"40) Percentuale di famiglie di un componente"],"indicatori":[]}
for i in list:
    obj_2 = {}
    obj_2["sez"] = i.get("sez")
    for j in range(2,45):
        if (i.get(str(j))== None):
            continue
        else:
            obj_2[j-1] = i.get(str(j))
    obj_2["fasce"] = i.get("fasce")   
    obj_2["famiglie"] = i.get("famiglie")          
    indicatori.get("indicatori").append(obj_2)

temp = []
for i in dataset_censimento.get("features"): temp.append(i.get("properties").get("SEZ"))
temp = max(temp)
ordered = []

#Ordering dataset_censimento
for i in range (0, temp+1):
    for j in dataset_censimento.get("features"):
        if (j.get("properties").get("SEZ") == i):
            ordered.append(j)

#with open("Datasets/Censimento_Milano_2011/censimento_cleared.geojson", "x") as outfile:
#    json.dump(dataset_censimento, outfile, indent=1)
#with open("Datasets/Indicatori/indicatori_cleared.json", "x") as outfile:
#    json.dump(indicatori, outfile, indent=1)

#Append indicatori to Censimento dataset
ordered_2 = []
for i in indicatori.get("indicatori"):
    for j in ordered:
        if (int(i.get("sez")) == int(j.get("properties").get("SEZ"))):
            j["indicatori"] = i
            j["fasce"] = j["indicatori"].pop("fasce")
            j["famiglie"] = j["indicatori"].pop("famiglie")
            ordered_2.append(j)
 
#Remove "Sez" data from Indicatori
for i in ordered_2: i.get("indicatori").pop("sez")
dataset_censimento["features"] = ordered_2

with open("Datasets/dataset_completo.geojson", "x") as outfile:
    json.dump(dataset_censimento, outfile, indent=1)
