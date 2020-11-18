import json 
import uuid
import sys

def generate_member(age):
    person = {}
    person["uuid"] = str(uuid.uuid4())
    if (age == "0-19"):
        #TODO: Create method to assign randomly kids based on age groups availability
        pass
    person["age"] = age
    return person

censimento = json.load(open('Datasets/dataset_completo.geojson'))

#Sezione-based randomic family generator
settori = {}
id_familiare = 1
skipped = 0

for i in censimento.get("features"):

    #Remove malformed and/or empty sections
    if (i.get("properties").get("SEZ") == 54 or i.get("properties").get("SEZ") == 3233 or i.get("properties").get("SEZ") == 2785 or i.get("properties").get("SEZ") == 2842 or i.get("properties").get("SEZ") == 2873 or i.get("properties").get("SEZ") == 3042 or i.get("properties").get("SEZ") == 3581 or i.get("properties").get("SEZ") == 4145 or i.get("properties").get("SEZ") == 4339 or i.get("properties").get("SEZ") == 4797 or i.get("properties").get("SEZ") == 4982 or i.get("properties").get("SEZ") == 5669):
        continue
    if (i.get("properties").get("POP_2010") == 0 or i.get("indicatori").get("1") == '' or i.get("indicatori").get("1") == 0):
        continue

    #This section has a tot_popolazione and fasce miscount
    #if (i.get("properties").get("SEZ") == 277 or i.get("properties").get("SEZ") == 453  or i.get("properties").get("SEZ") == 510 or i.get("properties").get("SEZ") == 3580):
    #    continue

    #Sez-2350 has a mismatch in solo 65+ families
    if (i.get("properties").get("SEZ") == 2350):
        continue

    #Create shortcuts for quick access
    indicatori = i.get("indicatori")
    fasce = indicatori.pop("fasce")
    famiglie = indicatori.pop("famiglie")
    
    if (famiglie == None or fasce == None):
        continue

    tot_popolazione = 0
    for j in famiglie:
        if (j != "tot_famiglie"):
            tot_popolazione += int(j)*famiglie[j]

    fasce_pop = 0
    for j in fasce:
        fasce_pop += fasce[j]

    if (tot_popolazione != fasce_pop):
        skipped += 1
        continue


    #Start printing sections data
    print("Codice sezione:",i.get("properties").get("SEZ"))
    print("Popolazione:",tot_popolazione)
    print("Famiglie totali:",famiglie["tot_famiglie"])
    print("Numero medio di componenti delle famiglie:", i.get("indicatori").get("39"))
    POP_2010 = i.get("properties").get("POP_2010")
    edifici = round(POP_2010/i.get("indicatori").get("1"))
    appartamenti = round(edifici*i.get("indicatori").get("3"))
    if (appartamenti!=0):
        avg_ppa = POP_2010/appartamenti
        print("[EST] Numero di abitanti per appartamento ad uso residenziale:", avg_ppa)
    print("[EST] Numero di edifici ad uso residenziale:", edifici)
    print("[EST] Numero di abitazioni totali ad uso residenziale:", appartamenti)

    #ESTIMATED AGE GROUPS
    if (i.get("indicatori").get("25") != '' and i.get("indicatori").get("26") != ''):
        young = i.get("indicatori").get("25")
        old = i.get("indicatori").get("26")
        Y = old + young

        X = (100+Y)/100
        mid_percent = 100/X
        old_percent = old/X
        young_percent = young/X

        est_anziani = round((POP_2010/100)*(old_percent))
        est_giovani = round((POP_2010/100)*(young_percent))
        est_attivi = round((POP_2010/100)*mid_percent)

        #Clone POP_2010 and households for counting purposes
        tot_famiglie = famiglie.get("tot_famiglie")

        print("[EST] Abitanti nella fascia 15-64:", est_attivi)
        print("[EST] Abitanti < 15:", est_giovani)
        print("[EST] Abitanti > 65:", est_anziani)
        print("[EST] Over 65+ che vivono da soli:",round(((round((POP_2010/100)*(old_percent)))/100*float(i.get("indicatori").get("17")))))

    #TODO: Generate age groups based on 'fasce' data
    anziani = fasce.get("65-69") + fasce.get("70-74") + fasce.get("75-100")
    giovani = fasce.get("0-5") + fasce.get("5-9") + fasce.get("10-14") + fasce.get("15-19")
    attivi = tot_popolazione - (anziani + giovani)
    print("Range 0-19:", giovani)
    print("Range 20-64:", attivi)
    print("Range 64-100:",anziani)
    print("Over 65+ che vivono da soli:",round((anziani/100)*indicatori.get("17")))
    print("Composizione delle famiglie:",famiglie)

    generated_families = []

    #Generate solo 65+ families
    for j in range(0,round((anziani/100)*indicatori.get("17"))):
        fam = {}
        members = []
        members.append(generate_member("65+"))
        fam["family_id"] = id_familiare
        fam["members"] = members
        id_familiare += 1
        anziani -= 1 
        tot_popolazione -= 1
        famiglie["tot_famiglie"] -= 1
        famiglie["1"] -= 1
        generated_families.append(fam)

    #Generate families of one
    for j in range(0,famiglie["1"]):
        fam = {}
        members = []
        members.append(generate_member("20-64"))
        fam["family_id"] = id_familiare
        fam["members"] = members
        id_familiare += 1
        attivi -= 1 
        tot_popolazione -= 1
        famiglie["tot_famiglie"] -= 1
        famiglie["1"] -= 1
        generated_families.append(fam)

    #Generate families of 2 components
    #Split in two, since families of two are frequent in 65+
    for j in range(0,famiglie["2"]):
        fam = {}
        members = []
        if (anziani > 1):
            members.append(generate_member("65+"))
            members.append(generate_member("65+"))
            anziani -= 2
            fam["family_id"] = id_familiare
            fam["members"] = members
            id_familiare += 1
            famiglie["tot_famiglie"] -= 1
            famiglie["2"] -= 1
            tot_popolazione -= 2
            generated_families.append(fam)

    #Generate families of 2 out of one-parent families
    for j in range(0,round((giovani/100)*indicatori.get("14"))):
        fam = {}
        members = []
        #If there are no parents, create families of kids and grandparents
        if (attivi > 0):
            members.append(generate_member("20-64"))
            attivi -= 1
            #TODO: Check for more data, not sure this is good
            if (famiglie["6"] != 0 and giovani > 4):
                if (giovani > 2 and anziani > 1):
                    members.append(generate_member("0-19"))
                    members.append(generate_member("0-19"))
                    members.append(generate_member("0-19"))
                    members.append(generate_member("65+"))
                    members.append(generate_member("65+"))
                    giovani -= 3
                    anziani -= 2
                elif (giovani > 3 and anziani > 0):
                    members.append(generate_member("0-19"))
                    members.append(generate_member("0-19"))
                    members.append(generate_member("0-19"))
                    members.append(generate_member("0-19"))
                    members.append(generate_member("65+"))
                    giovani -= 4
                    anziani -= 1
                elif (giovani > 4 and anziani == 0):
                    members.append(generate_member("0-19"))
                    members.append(generate_member("0-19"))
                    members.append(generate_member("0-19"))
                    members.append(generate_member("0-19"))
                    members.append(generate_member("0-19"))
                    giovani -= 5
                famiglie["6"] -= 1
                tot_popolazione -= 6
            elif (famiglie["5"] != 0 and giovani > 3):
                if (giovani > 1 and anziani > 1):
                    members.append(generate_member("0-19"))
                    members.append(generate_member("0-19"))
                    members.append(generate_member("65+"))
                    members.append(generate_member("65+"))
                    giovani -= 2
                    anziani -= 2
                elif (giovani > 2 and anziani > 0):
                    members.append(generate_member("0-19"))
                    members.append(generate_member("0-19"))
                    members.append(generate_member("0-19"))
                    members.append(generate_member("65+"))
                    giovani -= 3
                    anziani -= 1
                elif (giovani > 3):
                    members.append(generate_member("0-19"))
                    members.append(generate_member("0-19"))
                    members.append(generate_member("0-19"))
                    members.append(generate_member("0-19"))
                    giovani -= 4
                famiglie["5"] -= 1
                tot_popolazione -= 5
            elif (famiglie["4"] != 0):
                if (giovani > 0 and anziani > 1):
                    members.append(generate_member("0-19"))
                    members.append(generate_member("65+"))
                    members.append(generate_member("65+"))
                    giovani -= 1
                    anziani -= 2
                elif (giovani > 1 and anziani > 0):
                    members.append(generate_member("0-19"))
                    members.append(generate_member("0-19"))
                    members.append(generate_member("65+"))
                    giovani -= 2
                    anziani -= 1
                elif (giovani > 2):
                    members.append(generate_member("0-19"))
                    members.append(generate_member("0-19"))
                    members.append(generate_member("0-19"))
                    giovani -= 3
                else:
                    attivi += 1
                    break
                famiglie["4"] -= 1
                tot_popolazione -= 4
            elif (famiglie["3"] != 0):
                if (giovani > 0 and anziani > 0):
                    members.append(generate_member("0-19"))
                    members.append(generate_member("65+"))
                    giovani -= 1
                    anziani -= 1
                elif (giovani > 1):
                    members.append(generate_member("0-19"))
                    members.append(generate_member("0-19"))
                    giovani -= 2
                else:
                    attivi += 1
                    break
                famiglie["3"] -= 1
                tot_popolazione -= 3
            elif (famiglie["2"] != 0 and giovani > 0):
                members.append(generate_member("0-19"))
                famiglie["2"] -= 1
                tot_popolazione -= 2      
                giovani -= 1
            if (len(members) != 1):
                fam["family_id"] = id_familiare
                fam["members"] = members
                id_familiare += 1
                famiglie["tot_famiglie"] -= 1
                generated_families.append(fam)
            else:
                attivi += 1
                break
        else:
            break

    #Allocate 0-19 to families
    for j in range(0,giovani):
        fam = {}
        members = []
        #If there are no parents, create families of kids and grandparents
        if (attivi > 1):
            members.append(generate_member("20-64"))
            members.append(generate_member("20-64"))
            attivi -= 2
        elif (attivi > 0 and anziani > 0):
            members.append(generate_member("20-64"))
            members.append(generate_member("65+"))
            attivi -= 1
            anziani -= 1
        elif (anziani > 1):
            members.append(generate_member("65+"))
            members.append(generate_member("65+"))
            anziani -= 2
        #TODO: Check for more data, not sure this is good
        if (famiglie["6"] != 0 and giovani > 3):
            if (giovani > 3):
                members.append(generate_member("0-19"))
                members.append(generate_member("0-19"))
                members.append(generate_member("0-19"))
                members.append(generate_member("0-19"))
                giovani -= 4
            elif (giovani > 2 and anziani > 0):
                members.append(generate_member("0-19"))
                members.append(generate_member("0-19"))
                members.append(generate_member("0-19"))
                members.append(generate_member("65+"))
                giovani -= 3
                anziani -= 1
            elif (giovani > 1 and anziani > 1):
                members.append(generate_member("0-19"))
                members.append(generate_member("0-19"))
                members.append(generate_member("65+"))
                members.append(generate_member("65+"))
                giovani -= 2
                anziani -= 2
            famiglie["6"] -= 1
            tot_popolazione -= 6
        elif (famiglie["5"] != 0 and giovani > 2):
            if (giovani > 2):
                members.append(generate_member("0-19"))
                members.append(generate_member("0-19"))
                members.append(generate_member("0-19"))
                giovani -= 3
            elif (giovani > 1 and anziani > 0):
                members.append(generate_member("0-19"))
                members.append(generate_member("0-19"))
                members.append(generate_member("65+"))
                giovani -= 2
                anziani -= 1
            elif (giovani > 0 and anziani > 1):
                members.append(generate_member("0-19"))
                members.append(generate_member("65+"))
                members.append(generate_member("65+"))
                giovani -= 1
                anziani -= 2
            famiglie["5"] -= 1
            tot_popolazione -= 5
        elif (famiglie["4"] != 0 and giovani > 1):
            if (giovani > 1):
                members.append(generate_member("0-19"))
                members.append(generate_member("0-19"))
                giovani -= 2
            elif (giovani > 0 and anziani > 0):
                members.append(generate_member("0-19"))
                members.append(generate_member("65+"))
                giovani -= 1
                anziani -= 1
            famiglie["4"] -= 1
            tot_popolazione -= 4
        elif (famiglie["3"] != 0 and giovani > 0):
            members.append(generate_member("0-19"))
            giovani -= 1
            famiglie["3"] -= 1
            tot_popolazione -= 3
        if (len(members) > 2):
            fam["family_id"] = id_familiare
            fam["members"] = members
            id_familiare += 1
            famiglie["tot_famiglie"] -= 1
            generated_families.append(fam)
        else:
            for k in members:
                if (k.get("age") == "20-64"):
                    attivi += 1
                elif (k.get("age") == "65+"):
                    anziani += 1

    #Complete remaining families of 2
    for j in range(0,famiglie["2"]):
        fam = {}
        members = []
        if (anziani > 0 and attivi > 0):
            members.append(generate_member("65+"))
            members.append(generate_member("20-64"))
            anziani -= 1
            attivi -= 1
        elif (anziani == 0 and attivi > 1):
            members.append(generate_member("20-64"))
            members.append(generate_member("20-64"))
            attivi -= 2
        elif (giovani == 1 and attivi > 0):
            members.append(generate_member("0-19"))
            members.append(generate_member("20-64"))
            attivi -= 1
            giovani -= 1
        elif (giovani == 1 and anziani > 0):
            members.append(generate_member("0-19"))
            members.append(generate_member("65+"))
            anziani -= 1
            giovani -= 1
        fam["family_id"] = id_familiare
        fam["members"] = members
        id_familiare += 1
        famiglie["tot_famiglie"] -= 1
        famiglie["2"] -= 1
        tot_popolazione -= 2
        generated_families.append(fam)

    #Generate families of 3 components
    for j in range(0,famiglie["3"]):
        fam = {}
        members = []
        if (giovani == 1 and attivi > 1):
            #In case we're left with one under-19, allocate it here
            members.append(generate_member("20-64"))
            members.append(generate_member("20-64"))
            members.append(generate_member("0-19"))
            attivi -= 2
            giovani -= 1
        elif (attivi > 2 and anziani == 0):
            members.append(generate_member("20-64"))
            members.append(generate_member("20-64"))
            members.append(generate_member("20-64"))
            attivi -= 3
        elif (attivi > 1 and anziani > 0):
            members.append(generate_member("20-64"))
            members.append(generate_member("20-64"))
            members.append(generate_member("65+"))
            attivi -= 2
            anziani -= 1
        elif (attivi > 0 and anziani > 1):
            members.append(generate_member("20-64"))
            members.append(generate_member("65+"))
            members.append(generate_member("65+"))
            attivi -= 1
            anziani -= 2
        elif (attivi == 0 and anziani > 2):
            members.append(generate_member("65+"))
            members.append(generate_member("65+"))
            members.append(generate_member("65+"))
            anziani -= 3
        fam["family_id"] = id_familiare
        fam["members"] = members
        id_familiare += 1
        famiglie["tot_famiglie"] -= 1
        famiglie["3"] -= 1
        tot_popolazione -= 3
        generated_families.append(fam)

   #Generate families of 4 components
    for j in range(0,famiglie["4"]):
        fam = {}
        members = []
        if (giovani == 1 and attivi > 1):
            #In case we're left with one under-19, allocate it here
            members.append(generate_member("20-64"))
            members.append(generate_member("20-64"))
            members.append(generate_member("20-64"))
            members.append(generate_member("0-19"))
            attivi -= 3
            giovani -= 1
        elif (anziani == 1 and attivi > 1):
            #In case we're left with one 65+, allocate it here
            members.append(generate_member("20-64"))
            members.append(generate_member("20-64"))
            members.append(generate_member("20-64"))
            members.append(generate_member("65+"))
            attivi -= 3
            anziani -= 1
        elif (attivi > 3 and anziani == 0):
            members.append(generate_member("20-64"))
            members.append(generate_member("20-64"))
            members.append(generate_member("20-64"))
            members.append(generate_member("20-64"))
            attivi -= 4
        elif (attivi > 2 and anziani > 0):
            members.append(generate_member("20-64"))
            members.append(generate_member("20-64"))
            members.append(generate_member("20-64"))
            members.append(generate_member("65+"))
            attivi -= 3
            anziani -= 1
        elif (attivi > 1 and anziani > 1):
            print("This should not happen.")
            #sys.exit()
            members.append(generate_member("20-64"))
            members.append(generate_member("20-64"))
            members.append(generate_member("65+"))
            members.append(generate_member("65+"))
            attivi -= 2
            anziani -= 2
        elif (attivi > 0 and anziani > 2):
            print("This should not happen.")
            #sys.exit()
            members.append(generate_member("20-64"))
            members.append(generate_member("65+"))
            members.append(generate_member("65+"))
            members.append(generate_member("65"))
            attivi -= 1
            anziani -= 3
        elif (attivi == 0 and anziani > 3):
            print("This should not happen.")
            #sys.exit()
            members.append(generate_member("65+"))
            members.append(generate_member("65+"))
            members.append(generate_member("65+"))
            members.append(generate_member("65+"))
            anziani -= 4
        fam["family_id"] = id_familiare
        fam["members"] = members
        id_familiare += 1
        famiglie["tot_famiglie"] -= 1
        famiglie["4"] -= 1
        tot_popolazione -= 4
        generated_families.append(fam)

    #Generate families of 5 components
    for j in range(0,famiglie["5"]):
        fam = {}
        members = []
        if (giovani == 1 and attivi > 1):
            #In case we're left with one under-19, allocate it here
            members.append(generate_member("20-64"))
            members.append(generate_member("20-64"))
            members.append(generate_member("20-64"))
            members.append(generate_member("20-64"))
            members.append(generate_member("0-19"))
            attivi -= 4
            giovani -= 1
        elif (giovani == 2 and attivi > 1):
            #In case we're left with two under-19, allocate it here
            members.append(generate_member("20-64"))
            members.append(generate_member("20-64"))
            members.append(generate_member("20-64"))
            members.append(generate_member("0-19"))
            members.append(generate_member("0-19"))
            attivi -= 3
            giovani -= 2
        elif (anziani == 1 and attivi > 1):
            #In case we're left with one 65+, allocate it here
            members.append(generate_member("20-64"))
            members.append(generate_member("20-64"))
            members.append(generate_member("20-64"))
            members.append(generate_member("20-64"))
            members.append(generate_member("65+"))
            attivi -= 4
            anziani -= 1
        else:
            members.append(generate_member("20-64"))
            members.append(generate_member("20-64"))
            members.append(generate_member("20-64"))
            members.append(generate_member("20-64"))
            members.append(generate_member("20-64"))
            attivi -= 5
        fam["family_id"] = id_familiare
        fam["members"] = members
        id_familiare += 1
        famiglie["tot_famiglie"] -= 1
        famiglie["5"] -= 1
        tot_popolazione -= 5
        generated_families.append(fam)

    #Generate families of 6 components
    for j in range(0,famiglie["6"]):
        fam = {}
        members = []
        if (giovani == 1 and attivi > 1):
            #In case we're left with one under-19, allocate it here
            members.append(generate_member("20-64"))
            members.append(generate_member("20-64"))
            members.append(generate_member("20-64"))
            members.append(generate_member("20-64"))
            members.append(generate_member("20-64"))
            members.append(generate_member("0-19"))
            attivi -= 5
            giovani -= 1
        elif (anziani == 1 and attivi > 1):
            #In case we're left with one 65+, allocate it here
            members.append(generate_member("20-64"))
            members.append(generate_member("20-64"))
            members.append(generate_member("20-64"))
            members.append(generate_member("20-64"))
            members.append(generate_member("20-64"))
            members.append(generate_member("65+"))
            attivi -= 5
            anziani -= 1
        else:
            members.append(generate_member("20-64"))
            members.append(generate_member("20-64"))
            members.append(generate_member("20-64"))
            members.append(generate_member("20-64"))
            members.append(generate_member("20-64"))
            members.append(generate_member("20-64"))
            attivi -= 6
        fam["family_id"] = id_familiare
        fam["members"] = members
        id_familiare += 1
        famiglie["tot_famiglie"] -= 1
        famiglie["6"] -= 1
        tot_popolazione -= 6
        generated_families.append(fam)

    print()
    print()
    print("---")
    print("Giovani:",giovani)
    print("Attivi:",attivi)
    print("Anziani:",anziani)
    print("Famiglie:",famiglie)
    print("Popolazione rimasta:",tot_popolazione)
    print("---")
    print()
    print()

    #Check that all members of the i-sezione have been allocated to a family
    if (anziani != 0 or giovani != 0 or attivi != 0 or tot_popolazione != 0):
        #print(json.dumps(generated_families, indent=4, sort_keys=True))
        #print(generated_families)
        print("Skipped:",skipped)
        sys.exit("BINGO I FUCKED UP: Popolation Count Mismatch")
    
    for j in famiglie:
        if (famiglie[j] == 0):
            pass
        else:
            #print(json.dumps(generated_families, indent=4, sort_keys=True))
            #print(generated_families)
            print("Skipped:",skipped)
            print(famiglie)
            sys.exit("BINGO I FUCKED UP: Family Mismatch")

print("Sezioni saltate per via di malformazioni tra famiglie e fasce:",skipped)


