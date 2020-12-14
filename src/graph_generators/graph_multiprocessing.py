from pymongo import MongoClient
import networkx as nx
from multiprocessing import Pool
import psutil
import gc

def keyPresent(keys,word):
    for i in keys:
        if (i == word):
            return True
    return False

def generateFamilyClique(fam):
    fam_graph = nx.Graph()
    for mem in fam["members"]:
        fam_graph.add_node(mem["uuid"])
    G = (nx.complete_graph(list(fam_graph.nodes())))
    return G

def graphSez(l):
    generated_graph = nx.Graph()
    for index in l:
        #print("Current section:",index["properties"]["SEZ"],"/",max_sez, end="\r", flush=True)
        if (keyPresent(index.keys(),"famiglie") == True):
            for fam in index["famiglie"]:
                clique = generateFamilyClique(fam)
                generated_graph.add_nodes_from(clique.nodes())
                generated_graph.add_edges_from(clique.edges())
    return generated_graph

def graphWorkers(l):
    edges = []
    for i in l:
        #print("Current section:",i["properties"]["SEZ"],"/",max_sez, end="\r", flush=True)
        if (keyPresent(i.keys(),"lavoratori") == True):
            g = nx.erdos_renyi_graph(len(i["lavoratori"]),0.1)
            mapped = {}
            for index in range(0,len(i["lavoratori"])):
                mapped[list(g.nodes())[index]] = i["lavoratori"][index]
            g_2 = nx.relabel_nodes(g, mapped)
            for e in g_2.edges():edges.append(e) 
    return edges

client = MongoClient('localhost', 27017)
db = client['tesi']
db_sezioni = db['sezioni']
db_infanzia = db['scuole_infanzia']
db_elementari = db['scuole_elementari']
db_medie = db['scuole_medie']
db_superiori = db['scuole_superiori']

graph = nx.Graph()
print("Generating graph.")

sez = list(db_sezioni.find())
#max_sez = max([i["properties"]["SEZ"] for i in sez])

print("Starting pool")
cpu_processes = int(psutil.cpu_count()/2)
chunks = [sez[i::cpu_processes] for i in range(cpu_processes)]
print(len(chunks))
pool = Pool(processes=cpu_processes)

for i in pool.map(graphSez, chunks):
    graph.add_nodes_from(i.nodes())
    graph.add_edges_from(i.edges())


print("Creating scuole_infanzia layer edges...")
school_size = len(list(db_infanzia.find()))
for i in list(db_infanzia.find()):
    print("Current school:",list(db_infanzia.find()).index(i),"/",school_size, end="\r", flush=True)
    for classe in i["classi"]:
        for alunno in classe["alunni"]:
            for alunno_next in classe["alunni"]:
                graph.add_edge(alunno,alunno_next)

print("Creating scuole_elementari layer edges...")
school_size = len(list(db_elementari.find()))
for i in list(db_elementari.find()):
    print("Current school:",list(db_elementari.find()).index(i),"/",school_size, end="\r", flush=True)
    for classe in i["classi"]:
        for alunno in classe["alunni"]:
            for alunno_next in classe["alunni"]:
                graph.add_edge(alunno,alunno_next)

print("Creating scuole_media layer edges...")
school_size = len(list(db_medie.find()))
for i in list(db_medie.find()):
    print("Current school:",list(db_medie.find()).index(i),"/",school_size, end="\r", flush=True)
    for classe in i["classi"]:
        for alunno in classe["alunni"]:
            for alunno_next in classe["alunni"]:
                graph.add_edge(alunno,alunno_next)

print("Creating scuole_superiori layer edges...")
school_size = len(list(db_superiori.find()))
for i in list(db_superiori.find()):
    print("Current school:",list(db_superiori.find()).index(i),"/",school_size, end="\r", flush=True)
    for classe in i["classi"]:
        for alunno in classe["alunni"]:
            for alunno_next in classe["alunni"]:
                graph.add_edge(alunno,alunno_next)

del(db_elementari)
del(db_infanzia)
del(db_medie)
del(db_superiori)
del(db_sezioni)
del(sez)
del(classe)

print("Now generating workers") 
for i in pool.map(graphWorkers, chunks):
    graph.add_edges_from(i) 
gc.collect()
del(pool)
del(chunks)
#del(graph)

print("Done")
print(len(graph.nodes()))
print(len(graph.edges()))
nx.write_gml(graph, "dataset.gml")