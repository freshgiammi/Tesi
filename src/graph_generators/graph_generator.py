from pymongo import MongoClient
import networkx as nx

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

def generateClassClique(cl):
    class_graph = nx.Graph()
    for alunno in cl["alunni"]:
        class_graph.add_node(alunno)
    G = (nx.complete_graph(list(class_graph.nodes())))
    return list(G.edges())

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
max_sez = max([i["properties"]["SEZ"] for i in sez])

print("Creating nodes and family layers edges...")
for i in sez:
    print("Current section:",i["properties"]["SEZ"],"/",max_sez, end="\r", flush=True)
    if (keyPresent(i.keys(),"famiglie") == True):
        for fam in i["famiglie"]:
            #print("Composing graph:",i["famiglie"].index(fam))
            #graph = nx.compose(graph, generateFamilyClique(fam))
            #print("graph composed")
            generated_graph = generateFamilyClique(fam)
            graph.add_nodes_from(generated_graph.nodes())
            graph.add_edges_from(generated_graph.edges())

print("Creating scuole_infanzia layer edges...")
school_size = len(list(db_infanzia.find()))
for i in list(db_infanzia.find()):
    print("Current school:",list(db_infanzia.find()).index(i),"/",school_size, end="\r", flush=True)
    for classe in i["classi"]:
        graph.add_edges_from(generateClassClique(classe))

print("Creating scuole_elementari layer edges...")
school_size = len(list(db_elementari.find()))
for i in list(db_elementari.find()):
    print("Current school:",list(db_elementari.find()).index(i),"/",school_size, end="\r", flush=True)
    for classe in i["classi"]:
        graph.add_edges_from(generateClassClique(classe))

print("Creating scuole_media layer edges...")
school_size = len(list(db_medie.find()))
for i in list(db_medie.find()):
    print("Current school:",list(db_medie.find()).index(i),"/",school_size, end="\r", flush=True)
    for classe in i["classi"]:
        graph.add_edges_from(generateClassClique(classe))

print("Creating scuole_superiori layer edges...")
school_size = len(list(db_superiori.find()))
for i in list(db_superiori.find()):
    print("Current school:",list(db_superiori.find()).index(i),"/",school_size, end="\r", flush=True)
    for classe in i["classi"]:
        graph.add_edges_from(generateClassClique(classe))

print("Creating workplace layer edges...")
for i in sez:
    print("Current section:",i["properties"]["SEZ"],"/",max_sez, end="\r", flush=True)
    if (keyPresent(i.keys(),"lavoratori") == True):
        g = nx.erdos_renyi_graph(len(i["lavoratori"]),0.1)
        mapped = {}
        for index in range(0,len(i["lavoratori"])):
            mapped[list(g.nodes())[index]] = i["lavoratori"][index]
        g_2 = nx.relabel_nodes(g, mapped)
        graph.add_edges_from(g_2.edges())
        #for lavoratore in i["lavoratori"]:
        #    for lavoratore_next in i["lavoratori"]:
        #        if (np.random.binomial(1, 0.1) == 1):
        #            if (graph.has_edge(lavoratore,lavoratore_next) == False and lavoratore != lavoratore_next):graph.add_edge(lavoratore,lavoratore_next)

del(db_elementari)
del(db_infanzia)
del(db_medie)
del(db_superiori)
del(db_sezioni)
del(sez)
del(classe)
del(g)
del(g_2)
del(generated_graph)
del(mapped)
del(max_sez)
del(school_size)
del(index)
del(fam)
del(i)


print("Removing self edges...")
graph.remove_edges_from(nx.selfloop_edges(graph))

#print("Converting to undirected graph...")
#graph = nx.convert_node_labels_to_integers(graph.to_undirected())

print("total nodes:",len(graph.nodes()))
print("total edges:",len(graph.edges()))

print("Generating GraphML...")
nx.write_gml(graph, "dataset.gml")
print("Done.")