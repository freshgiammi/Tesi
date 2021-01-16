import json 
import sys
import shortuuid
import numpy as np
from pymongo import MongoClient

def sequentialID():
    global lastid
    lastid = lastid + 1
    return lastid

def generate_member(age,quantity,memberlist,agegroup=None):
    for index in range(0,quantity): #Generate n-quantity members, with set age.
        person = {}
        #person["uuid"] = str(sequentialID())
        #UUID has a 59-byte size. It's been truncated but collision probability should still be low for our usecase. 
        person["uuid"] = shortuuid.uuid()[:10]
        if (age == "0-19"):
            young = {"0-5":agegroup["0-5"],"5-9":agegroup["5-9"],"10-14":agegroup["10-14"],"15-19":agegroup["15-19"]}
            young_percent = []
            for j in young:
                young_percent.append((young[j]/sum(young.values())))
            index = np.random.choice([0,1,2,3],1,p=young_percent)
            if (index == 0):
                age = "0-5"
                agegroup[age] -= 1
            if (index == 1):
                age = "5-9"
                agegroup[age] -= 1
            if (index == 2):
                age = "10-14"
                agegroup[age] -= 1
            if (index == 3):
                age = "15-19"
                agegroup[age] -= 1
        person["age"] = age
        memberlist.append(person)
    return memberlist,agegroup

def generate_family(mem,id_fam,sez,giov,att,anz,pop,famiglie_db):
    fam = {}
    for i in mem:
        if (i.get("age") == "65+"):
            anz -= 1
        elif (i.get("age") == "20-64"):
            att -= 1
        elif (i.get("age") == "0-5" or i.get("age") == "5-9" or i.get("age") == "10-14" or i.get("age") == "15-19"):
            giov -= 1
    fam["family_id"] = id_fam
    fam["sez"] = sez
    fam["members"] = mem
    id_fam += 1
    pop -= len(mem)
    famiglie_db["tot_famiglie"] -= 1
    famiglie_db[str(len(mem))] -= 1
    if (debug == True):
        print("Last generated family has a size of ",len(mem))
        print(famiglie)
        print(fasce)
        print(fam)
        print(giovani,attivi,anziani)
    return fam, id_fam, giov, att, anz, pop, famiglie_db

censimento = json.load(open('Datasets/dataset_completo.geojson'))

#Sezione-based randomic family generator
client = MongoClient('localhost', 27017)
db = client['tesi']
collection = db['famiglie']
db_sezioni = db['sezioni']
debug = False

lastid = 0
simulated_distribution = []
id_familiare = 1
skipped = 0

for i in censimento.get("features"):

    #Sez-2350 has a mismatch in solo 65+ familiesd
    if (i.get("properties").get("SEZ") == 453 or i.get("properties").get("SEZ") == 2350 or i.get("properties").get("SEZ") == 3755 or i.get("properties").get("SEZ") == 4191 or i.get("properties").get("SEZ") == 5072):
        continue

    #Create shortcuts for quick access
    indicatori = i.get("indicatori")
    fasce = indicatori.pop("fasce")
    famiglie = indicatori.pop("famiglie")
    simulated = False

    #Major source of skipping: unable to generate
    if (famiglie == None or fasce == None):
        if debug == True: print("Unable to generate sez", i.get("properties").get("SEZ"),": one or more values missing.")
        if i.get("properties").get("POP_2010") != 0: skipped += 1
        continue

    #Get popolation size
    popolazione_famiglie = 0
    for j in famiglie:
        if (j != "tot_famiglie"):
            popolazione_famiglie += int(j)*famiglie[j]
    popolazione_fasce = sum(fasce.values())
    
    #If the two datasets have different popolation sizes, create fasce by proportionally reallocating members based on family sizes and fasce distribution
    if (popolazione_famiglie != popolazione_fasce):
        if (debug == True): print("Simulating sezione..")
        fasce_percent = {}
        fasce_def = {}
        for j in fasce:
            fasce_percent[j] = (fasce[j]/popolazione_fasce)
        for j in fasce_percent:
            fasce_def[j] = 0
        
        flag = False
        while flag == False:
            for j in fasce_percent:
                #This is equivalent as using np.random.choice but more compact due to the size of pools, by getting p of a single pool
                fasce_def[j] += np.random.binomial(n=1,size=1,p=fasce_percent[j])[0]
                if (sum(fasce_def.values()) == popolazione_famiglie):
                    flag = True
                    break;
        
        simulated = True
        #TODO: Track simulated sezioni to get an estimate distance for age distribution
        fasce_def_percent = {}
        for f in fasce_def:
            fasce_def_percent[f] = fasce_def[f]/sum(fasce_def.values())
        #print(fasce_percent)
        #print(fasce_def_percent)
        #print(list(fasce.values()))
        #print(list(fasce_def.values()))

        diff = {}
        for f in fasce:
            diff[f] = fasce_percent[f]-fasce_def_percent[f]
        #This returns 100%
        #print(100-sum(diff.values()))

        simulated_distribution.append(np.mean(list(diff.values())))
        fasce = fasce_def
        #sys.exit()    

    #Start printing sections data
    print("Generating sezione:",i.get("properties").get("SEZ"), end="\r", flush=True)

    anziani = fasce.get("65-69") + fasce.get("70-74") + fasce.get("75-100")
    giovani = fasce.get("0-5") + fasce.get("5-9") + fasce.get("10-14") + fasce.get("15-19")
    attivi = fasce.get("20-24") + fasce.get("25-29") + fasce.get("30-34") + fasce.get("35-39") + fasce.get("40-44") + fasce.get("45-49") + fasce.get("50-54") + fasce.get("55-59") + fasce.get("60-64")
    
    if (debug == True):
        print()
        print("Popolazione:",popolazione_famiglie)  
        print("Famiglie totali:",famiglie["tot_famiglie"])
        print("Numero medio di componenti delle famiglie:", i.get("indicatori").get("39"))
        print("Range 0-19:", giovani)
        print("Range 20-64:", attivi)
        print("Range 64-100:",anziani)
        print("Over 65+ che vivono da soli:",round((anziani/100)*indicatori.get("17")))
        print("Composizione delle famiglie:",famiglie)
        print("Composizione delle fasce:",fasce)
        print("Totale popolazione:",sum(fasce.values()))
        print()

    generated_families = []

    #Generate solo 65+ families
    for j in range(0,round((anziani/100)*indicatori.get("17"))):
        members = []
        if (anziani > 0 and famiglie["1"] > 0):
            members = generate_member("65+",1,members)[0]
            fam, id_familiare, giovani, attivi, anziani, popolazione_famiglie, famiglie = generate_family(members,id_familiare,i.get("properties").get("SEZ"),giovani,attivi,anziani,popolazione_famiglie,famiglie)
            generated_families.append(fam)

    #Generate families of one
    for j in range(0,famiglie["1"]):
        members = []
        #If we're running simulations, break the one-65+ household indicator and allow for more families.
        if (simulated == True and anziani > 0):
            members = generate_member("65+",1,members)[0]
        elif (attivi > 0):
            members = generate_member("20-64",1,members)[0]
        fam, id_familiare, giovani, attivi, anziani, popolazione_famiglie, famiglie = generate_family(members,id_familiare,i.get("properties").get("SEZ"),giovani,attivi,anziani,popolazione_famiglie,famiglie)
        generated_families.append(fam)

    #Generate families of 2 components
    #Split in two, since families of two are frequent in 65+
    for j in range(0,famiglie["2"]):
        members = []
        if (anziani > 1):
            members = generate_member("65+",2,members)[0]
            fam, id_familiare, giovani, attivi, anziani, popolazione_famiglie, famiglie = generate_family(members,id_familiare,i.get("properties").get("SEZ"),giovani,attivi,anziani,popolazione_famiglie,famiglie)
            generated_families.append(fam)

    #Generate families of 2 out of one-parent families
    for j in range(0,round((giovani/100)*indicatori.get("14"))):
        members = []
        #If there are no parents, create families of kids and grandparents
        if (attivi > 0):
            members = generate_member("20-64",1,members)[0]
            attivi -= 1 # Temporarily remove for consistency
            if (famiglie["6"] > 0 and giovani > 4):
                if (giovani > 2 and anziani > 1):
                    members, fasce = generate_member("0-19",3,members,fasce)
                    members = generate_member("65+",2,members)[0]
                elif (giovani > 3 and anziani > 0):
                    members, fasce = generate_member("0-19",4,members,fasce)
                    members = generate_member("65+",1,members)[0]
                elif (giovani > 4 and anziani == 0):
                    members, fasce = generate_member("0-19",5,members,fasce)
            elif (famiglie["5"] > 0 and giovani > 3):
                if (giovani > 1 and anziani > 1):
                    members, fasce = generate_member("0-19",2,members,fasce)
                    members = generate_member("65+",2,members)[0]
                elif (giovani > 2 and anziani > 0):
                    members, fasce = generate_member("0-19",3,members,fasce)
                    members = generate_member("65+",1,members)[0]
                elif (giovani > 3):
                    members, fasce = generate_member("0-19",4,members,fasce)
            elif (famiglie["4"] > 0):
                if (giovani > 0 and anziani > 1):
                    members, fasce = generate_member("0-19",1,members,fasce)
                    members = generate_member("65+",2,members)[0]
                elif (giovani > 1 and anziani > 0):
                    members, fasce = generate_member("0-19",2,members,fasce)
                    members = generate_member("65+",1,members)[0]
                elif (giovani > 2):
                    members, fasce = generate_member("0-19",3,members,fasce)
            elif (famiglie["3"] > 0):
                if (giovani > 0 and anziani > 0):
                    members, fasce = generate_member("0-19",1,members,fasce)
                    members = generate_member("65+",1,members)[0]
                elif (giovani > 1):
                    members, fasce = generate_member("0-19",2,members,fasce)
            elif (famiglie["2"] > 0 and giovani > 0):
                members, fasce = generate_member("0-19",1,members,fasce)
            if (len(members) != 1):
                attivi +=1 # Add temp value back
                fam, id_familiare, giovani, attivi, anziani, popolazione_famiglie, famiglie = generate_family(members,id_familiare,i.get("properties").get("SEZ"),giovani,attivi,anziani,popolazione_famiglie,famiglie)
                generated_families.append(fam)
            else:
                attivi += 1
                break
        else:
            break

    #Allocate 0-19 to families
    for j in range(0,giovani):
        members = []
        #If there are no parents, create families of kids and grandparents
        if (attivi > 1):
            members = generate_member("20-64",2,members)[0]
            attivi -= 2
        elif (attivi > 0 and anziani > 0):
            members = generate_member("20-64",1,members)[0]
            members = generate_member("65+",1,members)[0]
            attivi -= 1
            anziani -= 1
        elif (anziani > 1):
            members = generate_member("65+",2,members)[0]
            anziani -= 2
        elif (attivi == 1 and popolazione_famiglie > 2 and simulated == True):
            members = generate_member("20-64",1,members)[0]
            attivi -= 1
        if (famiglie["6"] > 0 and giovani > 3):
            if (giovani > 3):
                members, fasce = generate_member("0-19",4,members,fasce)
            elif (giovani > 2 and anziani > 0):
                members, fasce = generate_member("0-19",3,members,fasce)
                members = generate_member("65+",1,members)[0]
            elif (giovani > 1 and anziani > 1):
                members, fasce = generate_member("0-19",2,members,fasce)
                members = generate_member("65+",2,members)[0]
        elif (famiglie["5"] > 0 and giovani > 2):
            if (giovani > 2):
                members, fasce = generate_member("0-19",3,members,fasce)
            elif (giovani > 1 and anziani > 0):
                members, fasce = generate_member("0-19",2,members,fasce)
                members = generate_member("65+",1,members)[0]
            elif (giovani > 0 and anziani > 1):
                members, fasce = generate_member("0-19",1,members,fasce)
                members = generate_member("65+",2,members)[0]
        elif (famiglie["4"] > 0 and giovani > 1):
            #SIM
            if (giovani > 2 and simulated == True and len(members) == 1):
                members, fasce = generate_member("0-19",3,members,fasce)
            elif (giovani > 1):
                members, fasce = generate_member("0-19",2,members,fasce)
            elif (giovani > 0 and anziani > 0):
                members, fasce = generate_member("0-19",1,members,fasce)
                members = generate_member("65+",1,members)[0]
        elif (famiglie["3"] > 0 and giovani > 0):
            #SIM
            if (giovani > 1 and simulated == True and len(members) == 1):
                members, fasce = generate_member("0-19",2,members,fasce)
            else:    
                members, fasce = generate_member("0-19",1,members,fasce)
        if (len(members) > 2):
            for k in members:
                if (k.get("age") == "20-64"):
                    attivi += 1
                elif (k.get("age") == "65+"):
                    anziani += 1
            fam, id_familiare, giovani, attivi, anziani, popolazione_famiglie, famiglie = generate_family(members,id_familiare,i.get("properties").get("SEZ"),giovani,attivi,anziani,popolazione_famiglie,famiglie)
            generated_families.append(fam)
        else:
            for k in members:
                if (k.get("age") == "20-64"):
                    attivi += 1
                elif (k.get("age") == "65+"):
                    anziani += 1

    #Complete remaining families of 2
    for j in range(0,famiglie["2"]):
        members = []
        if (anziani > 0 and attivi > 0):
            members = generate_member("65+",1,members)[0]
            members = generate_member("20-64",1,members)[0]
        elif (anziani == 0 and attivi > 1):
            members = generate_member("20-64",2,members)[0]
        elif (giovani == 1 and attivi > 0):
            members, fasce = generate_member("0-19",1,members,fasce)
            members = generate_member("20-64",1,members)[0]
        elif (giovani == 1 and anziani > 0):
            members, fasce = generate_member("0-19",1,members,fasce)
            members = generate_member("65+",1,members)[0]
        #SIM
        elif (giovani > 0 and attivi > 0 and simulated == True):
            members, fasce = generate_member("0-19",1,members,fasce)
            members = generate_member("20-64",1,members)[0]
        if (len(members) == 2):
            fam, id_familiare, giovani, attivi, anziani, popolazione_famiglie, famiglie = generate_family(members,id_familiare,i.get("properties").get("SEZ"),giovani,attivi,anziani,popolazione_famiglie,famiglie)
            generated_families.append(fam)

    #Generate families of 3 components
    for j in range(0,famiglie["3"]):
        members = []
        if (giovani == 1 and attivi > 1):
            #In case we're left with one under-19, allocate it here
            members = generate_member("20-64",2,members)[0]
            members, fasce = generate_member("0-19",1,members,fasce)
        elif (attivi > 2 and anziani == 0):
            members = generate_member("20-64",3,members)[0]
        elif (attivi > 1 and anziani > 0):
            members = generate_member("20-64",2,members)[0]
            members = generate_member("65+",1,members)[0]
        elif (attivi > 0 and anziani > 1):
            members = generate_member("20-64",1,members)[0]
            members = generate_member("65+",2,members)[0]
        elif (attivi == 0 and anziani > 2):
            members = generate_member("65+",3,members)[0]
        fam, id_familiare, giovani, attivi, anziani, popolazione_famiglie, famiglie = generate_family(members,id_familiare,i.get("properties").get("SEZ"),giovani,attivi,anziani,popolazione_famiglie,famiglie)
        generated_families.append(fam)

   #Generate families of 4 components
    for j in range(0,famiglie["4"]):
        members = []
        if (giovani == 1 and attivi > 1):
            #In case we're left with one under-19, allocate it here
            members = generate_member("20-64",3,members)[0]
            members, fasce = generate_member("0-19",1,members,fasce)
        elif (giovani == 1 and attivi > 0 and anziani > 1):
            #In case we're left with one under-19, allocate it here
            members = generate_member("20-64",1,members)[0]
            members = generate_member("65+",2,members)[0]
            members, fasce = generate_member("0-19",1,members,fasce)
        elif (anziani == 1 and attivi > 1):
            #In case we're left with one 65+, allocate it here
            members = generate_member("20-64",3,members)[0]
            members = generate_member("65+",1,members)[0]
        elif (attivi > 3 and anziani == 0):
            members = generate_member("20-64",4,members)[0]
        elif (attivi > 2 and anziani > 0):
            members = generate_member("20-64",3,members)[0]
            members = generate_member("65+",1,members)[0]
        elif (attivi > 1 and anziani > 1):
            if debug == True: print("This should not happen. Sez:",i.get("properties").get("SEZ"), "reported a 65+ overflow generation of a size 4 family. (-1)")
            #sys.exit()
            members = generate_member("20-64",2,members)[0]
            members = generate_member("65+",2,members)[0]
        elif (attivi > 0 and anziani > 2):
            if debug == True: print("This should not happen. Sez:",i.get("properties").get("SEZ"), "reported a 65+ overflow generation of a size 4 family. (-2)")
            #sys.exit()
            members = generate_member("20-64",1,members)[0]
            members = generate_member("65+",3,members)[0]
        elif (attivi == 0 and anziani > 3):
            if debug == True: print("This should not happen. Sez:",i.get("properties").get("SEZ"), "reported a 65+ overflow generation of a size 4 family. (-3)")
            #sys.exit()
            members = generate_member("65+",4,members)[0]
        fam, id_familiare, giovani, attivi, anziani, popolazione_famiglie, famiglie = generate_family(members,id_familiare,i.get("properties").get("SEZ"),giovani,attivi,anziani,popolazione_famiglie,famiglie)
        generated_families.append(fam)

    #Generate families of 5 components
    for j in range(0,famiglie["5"]):
        members = []
        if (anziani > 2 and attivi > 1 and simulated == True):
            #In case we're left with one under-19, allocate it here
            members = generate_member("65+",3,members)[0]
            members = generate_member("20-64",2,members)[0]
        elif (anziani > 4 and simulated == True):
            #In case we're left with one under-19, allocate it here
            members = generate_member("65+",5,members)[0]
        elif (anziani > 3 and attivi > 0 and simulated == True):
            #SEZ_3603
            members = generate_member("65+",4,members)[0]
            members = generate_member("20-64",1,members)[0]
        elif (giovani == 1 and attivi > 1 and anziani == 2):
            #This solves SEZ_4982
            members = generate_member("20-64",2,members)[0]
            members = generate_member("65+",2,members)[0]
            members, fasce = generate_member("0-19",1,members,fasce)
        elif (giovani == 1 and attivi > 1 and anziani == 1):
            #This solves SEZ_4982
            members = generate_member("20-64",3,members)[0]
            members = generate_member("65+",1,members)[0]
            members, fasce = generate_member("0-19",1,members,fasce)
        elif (giovani == 0 and attivi > 1 and anziani == 2):
            #This solves SEZ_4982
            members = generate_member("20-64",3,members)[0]
            members = generate_member("65+",2,members)[0]
        elif (giovani == 1 and attivi > 1):
            #In case we're left with one under-19, allocate it here
            members = generate_member("20-64",4,members)[0]
            members, fasce = generate_member("0-19",1,members,fasce)
        elif (giovani == 2 and attivi > 1):
            #In case we're left with two under-19, allocate it here
            members = generate_member("20-64",3,members)[0]
            members, fasce = generate_member("0-19",2,members,fasce)
        elif (anziani == 1 and attivi > 1):
            #In case we're left with one 65+, allocate it here
            members = generate_member("20-64",4,members)[0]
            members = generate_member("65+",1,members)[0]
        else:    
            members = generate_member("20-64",5,members)[0]
        fam, id_familiare, giovani, attivi, anziani, popolazione_famiglie, famiglie = generate_family(members,id_familiare,i.get("properties").get("SEZ"),giovani,attivi,anziani,popolazione_famiglie,famiglie)
        generated_families.append(fam)

    #Generate families of 6 components
    for j in range(0,famiglie["6"]):
        members = []
        if (giovani == 0 and attivi == 4 and anziani == 2):
            #This solves SEZ_54
            members = generate_member("20-64",4,members)[0]
            members = generate_member("65+",2,members)[0]
        elif (giovani == 1 and attivi > 1 and anziani == 0):
            #In case we're left with one under-19, allocate it here
            members = generate_member("20-64",5,members)[0]
            members, fasce = generate_member("0-19",1,members,fasce)
        elif (giovani == 1 and attivi > 1 and anziani == 1):
            #This solves SEZ_54
            members = generate_member("20-64",4,members)[0]
            members = generate_member("65+",1,members)[0]
            members, fasce = generate_member("0-19",1,members,fasce)
        elif (giovani == 1 and attivi > 1 and anziani == 3):
            #This solves SEZ_54
            members = generate_member("20-64",2,members)[0]
            members = generate_member("65+",3,members)[0]
            members, fasce = generate_member("0-19",1,members,fasce)
        elif (giovani == 2 and attivi > 1 and anziani == 0):
            #In case we're left with two under-19, allocate it here
            members = generate_member("20-64",4,members)[0]
            members, fasce = generate_member("0-19",2,members,fasce)
        elif (giovani == 2 and attivi > 1 and anziani == 1):
            #This solves SEZ_54
            members = generate_member("20-64",3,members)[0]
            members = generate_member("65+",1,members)[0]
            members, fasce = generate_member("0-19",2,members,fasce)
        elif (giovani == 2 and attivi > 1 and anziani == 2):
            #This solves SEZ_54
            members = generate_member("20-64",2,members)[0]
            members = generate_member("65+",2,members)[0]
            members, fasce = generate_member("0-19",2,members,fasce)
        elif (giovani == 3 and attivi > 1 and anziani == 1):
            #This solves SEZ_54
            members = generate_member("20-64",2,members)[0]
            members = generate_member("65+",1,members)[0]
            members, fasce = generate_member("0-19",3,members,fasce)
        elif (giovani == 3 and attivi == 1 and anziani > 1):
            #This solves SEZ_54
            members = generate_member("20-64",1,members)[0]
            members = generate_member("65+",2,members)[0]
            members, fasce = generate_member("0-19",3,members,fasce)
        elif (giovani == 3 and attivi > 1):
            #In case we're left with three under-19, allocate it here
            members = generate_member("20-64",3,members)[0]
            members, fasce = generate_member("0-19",3,members,fasce)
        elif (anziani == 1 and attivi > 1):
            #In case we're left with one 65+, allocate it here
            members = generate_member("20-64",5,members)[0]
            members = generate_member("65+",1,members)[0]
        else:
            members = generate_member("20-64",6,members)[0]
        fam, id_familiare, giovani, attivi, anziani, popolazione_famiglie, famiglie = generate_family(members,id_familiare,i.get("properties").get("SEZ"),giovani,attivi,anziani,popolazione_famiglie,famiglie)
        generated_families.append(fam)

    #Check that all members of the i-sezione have been allocated to a family
    if (anziani != 0 or giovani != 0 or attivi != 0 or popolazione_famiglie != 0):
        #TODO: Fix this, happens in a few simulated families
        if (anziani == 0 and giovani > 0 and attivi == 0):
            skipped += 1
        else:
            print("Skipped:",skipped)
            print(generated_families)
            if (debug == True):
                #DEBUG CODE SECTION START
                print()
                print()
                print("---")
                print("Giovani:",giovani)
                print("Attivi:",attivi)
                print("Anziani:",anziani)
                print("Famiglie:",famiglie)
                print("Popolazione rimasta:",popolazione_famiglie)
                print("---")
                print()
                #DEBUG CODE SECTION END
            sys.exit("BINGO I FUCKED UP: Popolation Count Mismatch")
    else:
        for family in generated_families:
            collection.insert_one(family)
            family.pop("sez")
            family.pop("_id")
        db_sezioni.find_one_and_update({'properties.SEZ':i.get("properties").get("SEZ") }, {'$set': {'famiglie': generated_families}})

print("Sezioni saltate per via di malformazioni tra famiglie e fasce:",skipped)
print("Sezioni simulate: ",len(simulated_distribution))
print(np.mean(simulated_distribution))



