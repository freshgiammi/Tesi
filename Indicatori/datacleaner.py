import json

dataset_indicatori = json.load(open('Indicatori/ds385_popolazione_indicatori_popolazione_famiglie_2011_breve-1.json'))
dataset_censimento = json.load(open('Censimento_Milano_2011/sezioni_censimento_2011.geojson'))

#Data reorganization
list = []

for i in dataset_indicatori:
    obj = {}
    for j in i:
        index = j.split(')',1)[0]
        if (index == "2" or index == "3" or index == "4" or index == "9" or index == "14" or index == "15" or index == "18" or index == "28" or index == "35" or index == "40" or index == "41"):
            obj[j.split(')',1)[0]] = i.get(j)
        elif (index == "1"):
            obj["sez"] = i.get(j)
        else:
            continue
    list.append(obj)

#Data sorting
indicatori = {"legenda":["1) Numero medio di residenti per edificio ad uso residenziale","2) Numero medio di abitazioni per edificio ad uso residenziale",
"3) Numero medio di abitazioni occupate da residenti per edificio ad uso residenziale","8) Percentuale di bambini in età prescolare","13) Percentuale di abitazioni non occupate",
"14) Percentuale di famiglie monogenitore","17) Percentuale di 65+ che vivono da soli","27) Percentuale di popolazione 15+ che percepisce reddito sul totale della popolazione 15+",
"34) Percentuale di popolazione residente che si sposta giornalmente per studio o lavoro","39) Numero medio di componenti delle famiglie",
"40) Percentuale di famiglie di un componente"],"indicatori":[]}
for i in list:
    obj_2 = {}
    for j in range(2,45):
        if (i.get(str(j))== None):
            continue
        else:
            obj_2[j-1] = i.get(str(j))
    obj_2["sez"]=i.get("sez")
    indicatori.get("indicatori").append(obj_2)

temp = []
for i in dataset_censimento.get("features"): temp.append(i.get("properties").get("SEZ"))
temp = max(temp)
ordered = []

for i in range (0, temp+1):
    for j in dataset_censimento.get("features"):
        if (j.get("properties").get("SEZ") == i):
            ordered.append(j)

#ordered_2 = []
#for i in indicatori.get("indicatori"):
#    for j in ordered:
#        if (int(i.get("sez")) == int(j.get("properties").get("SEZ"))):
#            j["indicatori"] = i
#            ordered_2.append(j)
#for i in ordered_2: i.get("indicatori").pop("sez")

dataset_censimento["features"] = ordered
with open("Censimento_Milano_2011/censimento_cleared.geojson", 'x') as outfile:
    json.dump(dataset_censimento, outfile, indent=1)
with open("Indicatori/indicatori_cleared.json", 'x') as outfile:
    json.dump(indicatori, outfile, indent=1)
