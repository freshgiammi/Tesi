import json
from pymongo import MongoClient
import pandas
import sys
from shapely.geometry import Point, Polygon

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
    points_infanzia[school.get("_id")] = [{"geom":point,"size":0}]
for school in list(db_elementari.find()):
    #print(school.get("geometry").get("coordinates"))
    point = Point(school.get("geometry").get("coordinates"))
    points_elementari[school.get("_id")] = [{"geom":point,"size":0}]
for school in list(db_medie.find()):
    #print(school.get("geometry").get("coordinates"))
    point = Point(school.get("geometry").get("coordinates"))
    points_medie[school.get("_id")] = [{"geom":point,"size":0}]
for school in list(db_superiori.find()):
    #print(school.get("geometry").get("coordinates"))
    point = Point(school.get("geometry").get("coordinates"))
    points_superiori[school.get("_id")] = [{"geom":point,"size":0}]
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
size_elem = round(count_inf/len(points_elementari))
size_med = round(count_inf/len(points_medie))
size_sup = round(count_inf/len(points_superiori))

print("Scolari all'infanzia",size_inf)
print("Scolari alle elementari",size_elem)
print("Scolari alle medie",size_med)
print("Scolari alle superiori",size_sup)

print("Done. Allocating school to under-19...")
sez_index = list(db_sezioni.find())
for i in sez_index:
    print("CURRENT SEZ:",i.get("properties").get("SEZ"))
    #print(i.get("properties").get("SEZ"))
    if (i.get("famiglie")!= None):
        for family in i.get("famiglie"):
            for member in family.get("members"):
                if member.get("age") == "0-5":
                    for index in range(0,25):
                        if (points_infanzia[i.get("closest_schools").get("infanzia")[index]][0]["size"] < size_inf):
                            points_infanzia[i.get("closest_schools").get("infanzia")[index]][0]["size"] += 1
                            for x in list(db_sezioni.find({"_id":i.get("_id")})):
                                for mem in x["famiglie"][i["famiglie"].index(family)]["members"]:
                                    if (mem["uuid"] == member["uuid"]):
                                        mem["school"] = i.get("closest_schools").get("infanzia")[index]
                                #print(x["famiglie"])
                                db_sezioni.update_one({'_id': i.get("_id")}, {'$set': {'famiglie': x["famiglie"]}})
                            break
                        elif (index == 25 and points_infanzia[i.get("closest_schools").get("infanzia")[25]][0]["size"] >= size_inf):
                            print("UH OH")
                            sys.exit()
                        else:
                            continue
                elif member.get("age") == "5-9":
                    for index in range(0,25):
                        if (points_elementari[i.get("closest_schools").get("elementari")[index]][0]["size"] < size_elem):
                            points_elementari[i.get("closest_schools").get("elementari")[index]][0]["size"] += 1
                            for x in list(db_sezioni.find({"_id":i.get("_id")})):
                                for mem in x["famiglie"][i["famiglie"].index(family)]["members"]:
                                    if (mem["uuid"] == member["uuid"]):
                                        mem["school"] = i.get("closest_schools").get("elementari")[index]
                                #print(x["famiglie"])
                                db_sezioni.update_one({'_id': i.get("_id")}, {'$set': {'famiglie': x["famiglie"]}})
                            break
                        elif (index == 25 and points_elementari[i.get("closest_schools").get("elementari")[25]][0]["size"] >= size_elem):
                            print("UH OH")
                            sys.exit()
                        else:
                            continue
                elif member.get("age") == "10-14":
                    for index in range(0,25):    
                        if (points_medie[i.get("closest_schools").get("medie")[index]][0]["size"] < size_med):
                            points_medie[i.get("closest_schools").get("medie")[index]][0]["size"] += 1
                            for x in list(db_sezioni.find({"_id":i.get("_id")})):
                                for mem in x["famiglie"][i["famiglie"].index(family)]["members"]:
                                    if (mem["uuid"] == member["uuid"]):
                                        mem["school"] = i.get("closest_schools").get("medie")[index]
                                #print(x["famiglie"])
                                db_sezioni.update_one({'_id': i.get("_id")}, {'$set': {'famiglie': x["famiglie"]}})
                            break
                        elif (index == 25 and points_medie[i.get("closest_schools").get("medie")[25]][0]["size"] >= size_med):
                            print("UH OH")
                            sys.exit()
                        else:
                            continue
                elif member.get("age") == "15-19":
                    for index in range(0,25):    
                        if (points_superiori[i.get("closest_schools").get("superiori")[index]][0]["size"] < size_sup):
                            points_superiori[i.get("closest_schools").get("superiori")[index]][0]["size"] += 1
                            for x in list(db_sezioni.find({"_id":i.get("_id")})):
                                for mem in x["famiglie"][i["famiglie"].index(family)]["members"]:
                                    if (mem["uuid"] == member["uuid"]):
                                        mem["school"] = i.get("closest_schools").get("superiori")[index]
                                #print(x["famiglie"])
                                db_sezioni.update_one({'_id': i.get("_id")}, {'$set': {'famiglie': x["famiglie"]}})
                            break
                        elif (index == 25 and points_superiori[i.get("closest_schools").get("superiori")[25]][0]["size"] >= size_sup):
                            print("UH OH")
                            sys.exit()
                        else:
                            continue
    else:
        continue
print("Dumping to db done.")

#TODO: Allocate school _id to each under-19 member, and update size in scuole_*

#for i in points_infanzia:
#    print(points_infanzia[i][0]["size"])
#for i in points_elementari:
#    print(points_elementari[i][0]["size"])
#for i in points_medie:
#    print(points_medie[i][0]["size"])
#for i in points_superiori:
#    print(points_superiori[i][0]["size"])


