from pymongo import MongoClient

def isWorkAllocated(list,word):
    for i in list:
        if (i == word):
            return True
    return False

def allocateMember(family,work,age):
    flag = False
    for mem in family["members"]:
        if (mem["age"]==age and isWorkAllocated(mem.keys(),"sez_lavoro")==False):
            mem["sez_lavoro"] = int(work["sez_destinazione"])
            flag = True
            break
    return family, flag, mem

def workersListGenerator(database,member):
    for i in list(database.find({"properties.SEZ":member["sez_lavoro"]})):
        lavoratori = []
        for j in i.keys():
            if (j == "lavoratori"): lavoratori = i["lavoratori"]
        lavoratori.append(mem["uuid"])
    return lavoratori

client = MongoClient('localhost', 27017)
db = client['tesi']
db_sezioni = db['sezioni']
db_lavoro = db['lavoro']
for i in list(db_lavoro.find()):
    #TODO: Scroll through available work data
    for workplace in i["movimenti"]:
        print("Searching for spot in sez:",i["sez"])
        flag_allocated = False
        for wn in range(0,int(workplace["num"])):
            for j in list(db_sezioni.find({"properties.SEZ":i["sez"]})):
                #TODO: Check that sez actually has families inside
                allow = False
                for key in (j.keys()):
                    if (key == "famiglie"):
                        allow = True
                if (allow == True):
                    for fam in j["famiglie"]: #Look for spots in 20-64
                        j["famiglie"][j["famiglie"].index(fam)], flag_allocated, mem = allocateMember(fam,workplace,"20-64")
                        if (flag_allocated == True):
                            lavoratori = workersListGenerator(db_sezioni,mem)
                            db_sezioni.find_one_and_update({"properties.SEZ":i["sez"]},{"$set":{"famiglie":j["famiglie"]}})
                            db_sezioni.find_one_and_update({"properties.SEZ":mem["sez_lavoro"]},{"$set":{"lavoratori":lavoratori}})
                            break #Break loop until wn (inner loops are len=1), if member is found start looking for the next workplace
                    if (flag_allocated == False): 
                        for fam in j["famiglie"]: #Look for spots in 65+
                            j["famiglie"][j["famiglie"].index(fam)], flag_allocated, mem = allocateMember(fam,workplace,"65+")
                            if (flag_allocated == True):
                                lavoratori = workersListGenerator(db_sezioni,mem)
                                db_sezioni.find_one_and_update({"properties.SEZ":i["sez"]},{"$set":{"famiglie":j["famiglie"]}})
                                db_sezioni.find_one_and_update({"properties.SEZ":mem["sez_lavoro"]},{"$set":{"lavoratori":lavoratori}})
                                break #Break loop until wn (inner loops are len=1), if member is found start looking for the next workplace
            #If no member is available in the sez, clear remaining workplaces and switch to the next one.
            if (flag_allocated == False):
                print("Member not found on 20-64 and 65+ cycles. Cutoff workplaces. (Cycle is wn)")
                #TODO: Skip saving all other workplaces
                i["movimenti"][i["movimenti"].index(workplace)]["num"] == int(wn)
                db_lavoro.find_one_and_update({"sez":i["sez"]},{"$set":{"movimenti":i["movimenti"]}})
                break
        if (flag_allocated == False):
            print("Member not found on 20-64 and 65+ cycles. Cutoff workplaces. (Cycle is workplace)")
            #TODO: Skip saving all other workplaces
            break



            




