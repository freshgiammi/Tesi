import json
from pymongo import MongoClient
from shapely.geometry import Point, Polygon

def knearest (start, destinations, k):
    #Build array composed of id and distance to starting point, then sort the array by distance and return the first k elements.
    arr = {}
    for point in destinations:
        arr[point] = start.distance(destinations[point])
    sort = dict(sorted(arr.items(), key=lambda item: item[1]))
    return list(sort.keys())[:k]

client = MongoClient('localhost', 27017)
db = client['tesi']
db_famiglie = db['famiglie']
db_sezioni = db['sezioni']
db_infanzia = db['scuole_infanzia']
db_elementari = db['scuole_elementari']
db_medie = db['scuole_medie']
db_superiori = db['scuole_superiori']

infanzia = json.load(open('Datasets/Scuole/scuoleinfanzia_2012_2013.geojson'))
elementari = json.load(open('Datasets/Scuole/scuoleprimarie_2012_2013.geojson'))
medie = json.load(open('Datasets/Scuole/scuolesecondarie1grado_2012_2013.geojson'))
superiori = json.load(open('Datasets/Scuole/scuolesecondariesecondogrado.geojson'))

print("Indexing schools...")
points_infanzia = {}
points_elementari = {}
points_medie = {}
points_superiori = {}

for i in infanzia.get("features"):
    db_infanzia.insert_one(i)
    points_infanzia[i.get("_id")] = Point(i.get("geometry").get("coordinates"))
for i in elementari.get("features"):
    db_elementari.insert_one(i)
    points_elementari[i.get("_id")] = Point(i.get("geometry").get("coordinates"))
for i in medie.get("features"):
    db_medie.insert_one(i)
    points_medie[i.get("_id")] = Point(i.get("geometry").get("coordinates"))
for i in superiori.get("features"):
    db_superiori.insert_one(i)
    points_superiori[i.get("_id")] = Point(i.get("geometry").get("coordinates"))

print("Indexing schools done. Appending closest schools to sezioni...")
for i in list(db_sezioni.find()):
    #Insert closest schools 
    centroid = Polygon(i.get("geometry").get("coordinates")[0]).centroid
    #print(Polygon(i.get("geometry").get("coordinates")[0]))
    #closest_infanzia = min(points_infanzia.values(), key=Polygon(i.get("geometry").get("coordinates")[0]).distance)
    #closest_elementari = min(points_elementari.values(), key=Polygon(i.get("geometry").get("coordinates")[0]).distance)
    #closest_medie = min(points_medie.values(), key=Polygon(i.get("geometry").get("coordinates")[0]).distance)
    #closest_superiori = min(points_superiori.values(), key=Polygon(i.get("geometry").get("coordinates")[0]).distance)
    closest_schools = {"infanzia":knearest(centroid,points_infanzia,25),"elementari":knearest(centroid,points_elementari,25),"medie":knearest(centroid,points_medie,25),"superiori":knearest(centroid,points_superiori,25)}
    db_sezioni.update_one({'_id': i.get("_id")}, {'$set': {'closest_schools': closest_schools}})

print("Dumping to db done.")
