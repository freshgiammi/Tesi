import sys
import random
import string
from shapely.geometry import Point, Polygon
from pymongo import MongoClient

def nsplitter(total,range_start,range_end):
    splitted = []
    while (total > 0):
        if (total > range_start-1 and total < range_end+1):
            ran = total
            splitted.append(ran)
            total -= ran
        elif (total < range_start):
            while (total > 0):
                #START INJECTING UNITS INTO SMALLEST POOLS UNTIL WE RUN OUT OF UNITS
                index = splitted.index(min(splitted))
                splitted[index] += 1
                total -= 1
        else:
            ran = random.randint(15,25)
            splitted.append(ran)
            total -= ran
    if (total == 0):
        return splitted
    else:
        return "UH OH"

def main():
    client = MongoClient('localhost', 27017)
    db = client['tesi']
    db_famiglie = db['famiglie']
    db_sezioni = db['sezioni']

    print("Indexing schools...")
    points_infanzia = {}
    points_elementari = {}
    points_medie = {}
    points_superiori = {}
    db_infanzia = db['scuole_infanzia']
    db_elementari = db['scuole_elementari']
    db_medie = db['scuole_medie']
    db_superiori = db['scuole_superiori']

    for school in list(db_infanzia.find()):
        #print(school.get("geometry").get("coordinates"))
        point = Point(school.get("geometry").get("coordinates"))
        points_infanzia[school.get("_id")] = [{"geom":point,"size":0,"alunni":[],"classi":[]}]
    for school in list(db_elementari.find()):
        #print(school.get("geometry").get("coordinates"))
        point = Point(school.get("geometry").get("coordinates"))
        points_elementari[school.get("_id")] = [{"geom":point,"size":0,"alunni":[],"classi":[]}]
    for school in list(db_medie.find()):
        #print(school.get("geometry").get("coordinates"))
        point = Point(school.get("geometry").get("coordinates"))
        points_medie[school.get("_id")] = [{"geom":point,"size":0,"alunni":[],"classi":[]}]
    for school in list(db_superiori.find()):
        #print(school.get("geometry").get("coordinates"))
        point = Point(school.get("geometry").get("coordinates"))
        points_superiori[school.get("_id")] = [{"geom":point,"size":0,"alunni":[],"classi":[]}]
    print("Done. Calculating mean school size...")

    count_inf = 0
    count_elem = 0
    count_med = 0
    count_sup = 0
    for k in list(db_famiglie.find({},{"members.age":1,"_id":0})):
        for x in k.get("members"):
            if (x.get("age") == "0-5"):
                count_inf += 1
            elif (x.get("age") == "5-9"):
                count_elem += 1
            elif (x.get("age") == "10-14"):
                count_med += 1
            elif (x.get("age") == "15-19"):
                count_sup += 1

    #TODO: This doesn't match because it counts students from outside of Milan too, anything we can use this for?
    sum_sup = 0
    for k in list(db_superiori.find({})):
        sum_sup += k.get("properties").get("NUM_ISCR")
    #print(sum_sup)


    #print(count_inf)
    #print(count_elem)
    #print(count_med)
    #print(count_sup)
    size_inf = round(count_inf/len(points_infanzia))
    size_elem = round(count_elem/len(points_elementari))
    size_med = round(count_med/len(points_medie))
    size_sup = round(count_sup/len(points_superiori))

    print("Scolari all'infanzia",size_inf)
    print("Scolari alle elementari",size_elem)
    print("Scolari alle medie",size_med)
    print("Scolari alle superiori",size_sup)

    print("Done. Allocating school to under-19...")
    sez_index = list(db_sezioni.find())
    for i in sez_index:
        print("Current section:",i["properties"]["SEZ"],end="\r", flush=True)
        #print(i.get("properties").get("SEZ"))
        if (i.get("famiglie")!= None):
            for family in i.get("famiglie"):
                for member in family.get("members"):
                    if member.get("age") == "0-5":
                        for index in range(0,25):
                            if (points_infanzia[i.get("closest_schools").get("infanzia")[index]][0]["size"] < size_inf):
                                points_infanzia[i.get("closest_schools").get("infanzia")[index]][0]["size"] += 1
                                points_infanzia[i.get("closest_schools").get("infanzia")[index]][0]["alunni"].append(member.get("uuid"))
                                member["school"] = i.get("closest_schools").get("infanzia")[index]
                                db_sezioni.find_one_and_update({"_id":i.get("_id")},{"$set":{"famiglie":i.get("famiglie")}})
                            elif (index == 25 and points_infanzia[i.get("closest_schools").get("infanzia")[25]][0]["size"] >= size_inf):
                                print("UH OH")
                                sys.exit()
                            else:
                                continue
                    elif member.get("age") == "5-9":
                        for index in range(0,25):
                            if (points_elementari[i.get("closest_schools").get("elementari")[index]][0]["size"] < size_elem):
                                points_elementari[i.get("closest_schools").get("elementari")[index]][0]["size"] += 1
                                points_elementari[i.get("closest_schools").get("elementari")[index]][0]["alunni"].append(member.get("uuid"))
                                member["school"] = i.get("closest_schools").get("elementari")[index]
                                db_sezioni.find_one_and_update({"_id":i.get("_id")},{"$set":{"famiglie":i.get("famiglie")}})
                            elif (index == 25 and points_elementari[i.get("closest_schools").get("elementari")[25]][0]["size"] >= size_elem):
                                print("UH OH")
                                sys.exit()
                            else:
                                continue
                    elif member.get("age") == "10-14":
                        for index in range(0,25):    
                            if (points_medie[i.get("closest_schools").get("medie")[index]][0]["size"] < size_med):
                                points_medie[i.get("closest_schools").get("medie")[index]][0]["size"] += 1
                                points_medie[i.get("closest_schools").get("medie")[index]][0]["alunni"].append(member.get("uuid"))
                                member["school"] = i.get("closest_schools").get("medie")[index]
                                db_sezioni.find_one_and_update({"_id":i.get("_id")},{"$set":{"famiglie":i.get("famiglie")}})
                            elif (index == 25 and points_medie[i.get("closest_schools").get("medie")[25]][0]["size"] >= size_med):
                                print("UH OH")
                                sys.exit()
                            else:
                                continue
                    elif member.get("age") == "15-19":
                        for index in range(0,25):    
                            if (points_superiori[i.get("closest_schools").get("superiori")[index]][0]["size"] < size_sup):
                                points_superiori[i.get("closest_schools").get("superiori")[index]][0]["size"] += 1
                                points_superiori[i.get("closest_schools").get("superiori")[index]][0]["alunni"].append(member.get("uuid"))
                                member["school"] = i.get("closest_schools").get("superiori")[index]
                                db_sezioni.find_one_and_update({"_id":i.get("_id")},{"$set":{"famiglie":i.get("famiglie")}})
                            elif (index == 25 and points_superiori[i.get("closest_schools").get("superiori")[25]][0]["size"] >= size_sup):
                                print("UH OH")
                                sys.exit()
                            else:
                                continue
        else:
            continue
    print()
    print("Kids allocated to schools. Generating classes...")

    #TODO: Allocate school _id to each under-19 member, and update size in scuole_*
    for i in points_infanzia:
        split = nsplitter(points_infanzia[i][0]["size"],15,25)
        for j in split:
            classe = {"sezione":string.ascii_uppercase[split.index(j)],"alunni":[]}
            for k in range(0,j):
                pick = random.randint(0,len(points_infanzia[i][0]["alunni"])-1)
                classe["alunni"].append(points_infanzia[i][0]["alunni"].pop(pick))
            split[split.index(j)] = 0 #Sign as emptied
            #TODO: Fetch k uuids to create class
            points_infanzia[i][0]["classi"].append(classe)
        db_infanzia.find_one_and_update({"_id":i},{"$set":{"classi":points_infanzia[i][0]["classi"]}})

    for i in points_elementari:
        #print(points_elementari[i][0]["size"])
        class_size = int(points_elementari[i][0]["size"]/5)
        if (class_size*5 != points_elementari[i][0]["size"]):
            pool = [class_size,class_size,class_size,class_size,class_size]
            while (sum(pool) < points_elementari[i][0]["size"]):
                pool[pool.index(min(pool))] +=1
        else:
            pool = [class_size,class_size,class_size,class_size,class_size]        
        sez = 0
        for j in pool:
            sez += 1
            split = nsplitter(j,15,25)
            for k in split:
                classe = {"classe":sez,"sezione":string.ascii_uppercase[split.index(k)],"alunni":[]}
                for y in range(0,k):
                    pick = random.randint(0,len(points_elementari[i][0]["alunni"])-1)
                    classe["alunni"].append(points_elementari[i][0]["alunni"].pop(pick))
                split[split.index(k)] = 0 #Sign as emptied
                points_elementari[i][0]["classi"].append(classe)
        db_elementari.find_one_and_update({"_id":i},{"$set":{"classi":points_elementari[i][0]["classi"]}})

    for i in points_medie:
        #print(points_medie[i][0]["size"])
        class_size = int(points_medie[i][0]["size"]/3)
        if (class_size*3 != points_medie[i][0]["size"]):
            pool = [class_size,class_size,class_size]
            while (sum(pool) < points_medie[i][0]["size"]):
                pool[pool.index(min(pool))] +=1
        else:
            pool = [class_size,class_size,class_size]        
        sez = 0
        for j in pool:
            sez += 1
            split = nsplitter(j,15,25)
            for k in split:
                classe = {"classe":sez,"sezione":string.ascii_uppercase[split.index(k)],"alunni":[]}
                for y in range(0,k):
                    pick = random.randint(0,len(points_medie[i][0]["alunni"])-1)
                    classe["alunni"].append(points_medie[i][0]["alunni"].pop(pick))
                split[split.index(k)] = 0 #Sign as emptied
                points_medie[i][0]["classi"].append(classe)
        db_medie.find_one_and_update({"_id":i},{"$set":{"classi":points_medie[i][0]["classi"]}})

    for i in points_superiori:
        #print(points_superiori[i][0]["size"])
        class_size = int(points_superiori[i][0]["size"]/5)
        if (class_size*5 != points_superiori[i][0]["size"]):
            pool = [class_size,class_size,class_size,class_size,class_size]
            while (sum(pool) < points_superiori[i][0]["size"]):
                pool[pool.index(min(pool))] +=1
        else:
            pool = [class_size,class_size,class_size,class_size,class_size]        
        sez = 0
        for j in pool:
            sez += 1
            split = nsplitter(j,15,25)
            for k in split:
                classe = {"classe":sez,"sezione":string.ascii_uppercase[split.index(k)],"alunni":[]}
                for y in range(0,k):
                    pick = random.randint(0,len(points_superiori[i][0]["alunni"])-1)
                    classe["alunni"].append(points_superiori[i][0]["alunni"].pop(pick))
                split[split.index(k)] = 0 #Sign as emptied
                points_superiori[i][0]["classi"].append(classe)
        db_superiori.find_one_and_update({"_id":i},{"$set":{"classi":points_superiori[i][0]["classi"]}})

    print("Dumping to db done.")

if __name__ == "__main__":
    main()