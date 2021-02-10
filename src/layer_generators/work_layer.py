from numpy.core.numeric import False_
from pymongo import MongoClient
import json
import numpy as np
import os

def allocateMember(family,sez,age):
    flag = False
    alloc = False
    for mem in family["members"]:
        if "sez_lavoro" in mem.keys():
            alloc = True
        if (mem["age"]==age and alloc==False):
            mem["sez_lavoro"] = int(sez)
            flag = True
            break
    return family, flag, mem

def main():
    client = MongoClient('localhost', 27017)
    db = client['tesi']
    db_sezioni = db['sezioni']
    db_lavoro = db['lavoro']

    pendolarismo = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..', 'Datasets/Pendolarismo/ds390_Pendolarismo_entroMI_sezione.json')))
    
    sez_indexes = list(dict.fromkeys([i["Sezione di origine"] for i in pendolarismo]))
    sez_indexes.pop(sez_indexes.index(8888885))
    sez_indexes.pop(sez_indexes.index(8888886))
    sez_indexes.pop(sez_indexes.index(8888888))

    workers_destsez = {}
    for i in list(db_sezioni.find()):
        if (i["properties"]["SEZ"] == 8888885 or i["properties"]["SEZ"] == 8888886 or i["properties"]["SEZ"] == 8888888):
            continue
        workers_destsez[i["properties"]["SEZ"]] = [] 

    pendolarismo_clean = {} #{sez(int):list]}
    lavoro = []
    print("Indexing workplaces...")
    for i in list(dict.fromkeys([index["Sezione di origine"] for index in pendolarismo])):
        print("Indexing sez:",i, end="\r", flush=True)
        if (i == 8888885 or i == 8888886 or i == 8888888):
            continue
        pendolarismo_clean[i] = []
        for k in pendolarismo:
            #TODO: Simulate "sezione di destinazione" if it's not set
            if (i == k["Sezione di origine"] and k["Motivo"]!="Studio"):
                obj = {}
                #10k entries do not have a set destination, so pick one randomly from the set of sez defined
                if (k["Sezione di destinazione"]!="Non determinata"):
                    obj["sez_destinazione"] = k["Sezione di destinazione"]
                elif (k["Sezione di destinazione"]=="Non determinata"):
                    obj["sez_destinazione"] = str(np.random.choice(sez_indexes,1)[0])
                obj["motivo"] = k["Motivo"]
                obj["num"] = k["Numerositŕ"]
                pendolarismo_clean[i].append(obj)
        #Scroll through available work data
        for j in list(db_sezioni.find({"properties.SEZ":i})):
            goto_next = False
            if "famiglie" in j.keys():
                families = j["famiglie"]
                for movement in pendolarismo_clean[i]:
                    flag_allocated = False
                    if goto_next == True:
                        break #No more workers available, break out of this loop too, save everything and go to next sez
                    for wn in range(0,int(movement["num"])): #Num of movements to this sez
                        #print("Searching for spot in sez:",i)
                        for fam in families: #Look for spots in 20-64
                            families[families.index(fam)], flag_allocated, mem = allocateMember(fam,movement["sez_destinazione"],"20-64")
                            if (flag_allocated == True):
                                workers_destsez[mem["sez_lavoro"]].append(mem["uuid"])
                                break #Break out of families loop
                        if (flag_allocated == True):
                            continue #We have allocated, go to next wm iteration
                        elif (flag_allocated == False): 
                            for fam in families: #Look for spots in 65+
                                families[families.index(fam)], flag_allocated, mem = allocateMember(fam,movement["sez_destinazione"],"65+")
                                if (flag_allocated == True):
                                    workers_destsez[mem["sez_lavoro"]].append(mem["uuid"])
                                    break #Break out of families loop
                        #If flag is true, it means that 65+ has ben allocated. If false, we have run out of workers avauilable and should cutoff and go to the next sez
                        if (flag_allocated == True):
                            continue #We have allocated, go to next wm iteration
                        elif (flag_allocated == False):
                            #print("Member not found on 20-64 and 65+ cycles. Cutoff wm. (Cycle is wn)")
                            pendolarismo_clean[i][pendolarismo_clean[i].index(movement)]["num"] == int(wn)+1
                            obj = {"sez":i,"movimenti":[]}
                            for p in range (0, pendolarismo_clean[i].index(movement)):
                                obj["movimenti"].append(pendolarismo_clean[i][p])
                            lavoro.append(obj)
                            goto_next = True
                            break #Go to next movement, then trigger goto_next to escape work allocation
                #Update families
                if (goto_next == False):
                    obj = {"sez":i,"movimenti":[]}
                    for p in pendolarismo_clean[i]:
                        obj["movimenti"].append(p)
                    lavoro.append(obj)
                db_sezioni.find_one_and_update({"properties.SEZ":i},{"$set":{"famiglie":families}})
            else:
                #Set empty db_lavoro
                lavoro.append({"sez":i,"movimenti":[]})
    #Push lavoro to db_lavoro
    for i in lavoro:
        db_lavoro.insert_one({"sez":i["sez"],"movimenti":i["movimenti"]})

    #Push workers_destsez to db_sezioni
    for i in workers_destsez:
        db_sezioni.find_one_and_update({"properties.SEZ":i},{"$set":{"lavoratori":workers_destsez[i]}})

if __name__ == "__main__":
    main()