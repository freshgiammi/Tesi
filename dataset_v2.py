import json 
import uuid

censimento = json.load(open('Datasets/dataset_completo.geojson'))

#Sezione-based randomic family generator
settori = {}
id_familiare = 1

for i in censimento.get("features"):

    #Remove malformed and/or empty sections
    if (i.get("properties").get("SEZ") == 54 or i.get("properties").get("SEZ") == 3233 or i.get("properties").get("SEZ") == 2785 or i.get("properties").get("SEZ") == 2842 or i.get("properties").get("SEZ") == 2873 or i.get("properties").get("SEZ") == 3042 or i.get("properties").get("SEZ") == 3581 or i.get("properties").get("SEZ") == 4145 or i.get("properties").get("SEZ") == 4339 or i.get("properties").get("SEZ") == 4797 or i.get("properties").get("SEZ") == 4982 or i.get("properties").get("SEZ") == 5669):
        continue
    if (i.get("properties").get("POP_2010") == 0 or i.get("indicatori").get("1") == '' or i.get("indicatori").get("1") == 0):
        continue

    #Create shortcuts for quick access
    indicatori = i.get("indicatori")
    fasce = indicatori.pop("fasce")
    famiglie = indicatori.pop("famiglie")
    
    #Start printing sections data
    print("Codice sezione:",i.get("properties").get("SEZ"))
    POP_2010 = i.get("properties").get("POP_2010")
    edifici = round(POP_2010/i.get("indicatori").get("1"))
    appartamenti = round(edifici*i.get("indicatori").get("3"))
    print("Popolazione:",POP_2010)
    print("Numero di edifici ad uso residenziale:", edifici)
    print("Numero di abitazioni totali ad uso residenziale:", appartamenti)
    if (appartamenti!=0):
        avg_ppa = POP_2010/appartamenti
        print("Numero di abitanti per appartamento ad uso residenziale:", avg_ppa)
        print("Numero medio di componenti delle famiglie:", i.get("indicatori").get("39"))

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
        tot_popolazione = int(POP_2010)
        

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
        print("Over 65+ che vivono da soli:",round((anziani/100)*i.get("indicatori").get("17")))

        generated_families = []

        #Generate solo 65+ families
        for i in range(0,round((anziani/100)*i.get("indicatori").get("17"))):
            fam = {}
            members = []
            person = {}
            person["uuid"] = str(uuid.uuid4())
            person["age"] = "65+"
            fam["family_id"] = id_familiare
            members.append(person)
            fam["members"] = members
            id_familiare += 1
            anziani -= 1 
            tot_popolazione -= 1
            famiglie["tot_famiglie"] -= 1
            famiglie["1"] -= 1
            generated_families.append(fam)

        #Generate families of one
        for i in range(0,famiglie["1"]):
            fam = {}
            members = []
            person = {}
            person["uuid"] = str(uuid.uuid4())
            person["age"] = "20-64"
            fam["family_id"] = id_familiare
            members.append(person)
            fam["members"] = members
            id_familiare += 1
            attivi -= 1 
            tot_popolazione -= 1
            famiglie["tot_famiglie"] -= 1
            famiglie["1"] -= 1
            generated_families.append(fam)

        print(generated_families)
        print(famiglie["tot_famiglie"])
        break


