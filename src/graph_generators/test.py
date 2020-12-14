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
        fam_graph.add_node(int(mem["uuid"]))
    G = (nx.complete_graph(list(fam_graph.nodes())))
    return G

def generateClassClique(cl):
    class_graph = nx.Graph()
    for alunno in cl["alunni"]:
        class_graph.add_node(int(alunno))
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

nx.write_gml(graph, "dataset.gml")