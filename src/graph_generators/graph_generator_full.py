from pymongo import MongoClient
import networkx as nx
import numpy as np

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
    return G

def main(schools=True):

    client = MongoClient('localhost', 27017)
    db = client['tesi']
    db_sezioni = db['sezioni']
    db_infanzia = db['scuole_infanzia']
    db_elementari = db['scuole_elementari']
    db_medie = db['scuole_medie']
    db_superiori = db['scuole_superiori']

    graph = nx.Graph()
    print("Loading database into memory...")
    sez = list(db_sezioni.find())
    max_sez = max([i["properties"]["SEZ"] for i in sez])

    print("Creating nodes and family layers edges...")
    for i in sez:
        print("Current section:",i["properties"]["SEZ"],"/",max_sez, end="\r", flush=True)
        if (keyPresent(i.keys(),"famiglie") == True):
            for fam in i["famiglie"]:\
                #print("Composing graph:",i["famiglie"].index(fam))
                #graph = nx.compose(graph, generateFamilyClique(fam))
                #print("graph composed")
                generated_graph = generateFamilyClique(fam)
                graph.add_nodes_from(generated_graph.nodes())
                graph.add_edges_from(generated_graph.edges())
                if (len(list(generated_graph.edges()))) != 0:
                    for e in list(generated_graph.edges()):
                        graph.edges[e]['weight'] = 1
                for mem in fam["members"]:
                    graph.nodes[mem["uuid"]]['age'] = mem["age"]
                    graph.nodes[mem["uuid"]]['family_id'] = fam["family_id"]
                    #print(nx.get_edge_attributes(graph,'weight'))
                
    if schools==True:
        print("Generating schools layer...")
        print("Creating scuole_infanzia layer edges...")
        school_size = len(list(db_infanzia.find()))
        for i in list(db_infanzia.find()):
            #print("Current school:",list(db_infanzia.find()).index(i),"/",school_size, end="\r", flush=True)
            for classe in i["classi"]:
                generated_graph = generateClassClique(classe)
                graph.add_edges_from(generated_graph.edges())
                if (len(list(generated_graph.edges()))) != 0:
                    for e in list(generated_graph.edges()):
                        graph.edges[e]['weight'] = float(np.random.uniform(0.65,1,1)[0])
                    #print(nx.get_edge_attributes(graph,'weight'))

        print("Creating scuole_elementari layer edges...")
        school_size = len(list(db_elementari.find()))
        for i in list(db_elementari.find()):
            print("Current school:",list(db_elementari.find()).index(i),"/",school_size, end="\r", flush=True)
            for classe in i["classi"]:
                generated_graph = generateClassClique(classe)
                graph.add_edges_from(generated_graph.edges())
                if (len(list(generated_graph.edges()))) != 0:
                    for e in list(generated_graph.edges()):
                        graph.edges[e]['weight'] = float(np.random.uniform(0.65,1,1)[0])
                    #print(nx.get_edge_attributes(graph,'weight'))

        print("Creating scuole_media layer edges...")
        school_size = len(list(db_medie.find()))
        for i in list(db_medie.find()):
            print("Current school:",list(db_medie.find()).index(i),"/",school_size, end="\r", flush=True)
            for classe in i["classi"]:
                generated_graph = generateClassClique(classe)
                graph.add_edges_from(generated_graph.edges())
                if (len(list(generated_graph.edges()))) != 0:
                    for e in list(generated_graph.edges()):
                        graph.edges[e]['weight'] = float(np.random.uniform(0.65,1,1)[0])
                    #print(nx.get_edge_attributes(graph,'weight'))

        print("Creating scuole_superiori layer edges...")
        school_size = len(list(db_superiori.find()))
        for i in list(db_superiori.find()):
            print("Current school:",list(db_superiori.find()).index(i),"/",school_size, end="\r", flush=True)
            for classe in i["classi"]:
                generated_graph = generateClassClique(classe)
                graph.add_edges_from(generated_graph.edges())
                if (len(list(generated_graph.edges()))) != 0:
                    for e in list(generated_graph.edges()):
                        graph.edges[e]['weight'] = float(np.random.uniform(0.65,1,1)[0])
                    #print(nx.get_edge_attributes(graph,'weight'))

    else:
        print("School layer generation has been disabled.")
        
    print("Creating workplace layer edges...")
    for i in sez:
        print("Current section:",i["properties"]["SEZ"],"/",max_sez, end="\r", flush=True)
        if (keyPresent(i.keys(),"lavoratori") == True):
            g = nx.erdos_renyi_graph(len(i["lavoratori"]),0.15)
            mapped = {}
            for index in range(0,len(i["lavoratori"])):
                mapped[list(g.nodes())[index]] = i["lavoratori"][index]
            g_2 = nx.relabel_nodes(g, mapped)
            graph.add_edges_from(g_2.edges())
            if (len(list(g_2.edges()))) != 0:
                for e in list(g_2.edges()):
                    graph.edges[e]['weight'] = float(np.random.uniform(0.3,0.7,1)[0])
                #print(nx.get_edge_attributes(graph,'weight'))

            #for lavoratore in i["lavoratori"]:
            #    for lavoratore_next in i["lavoratori"]:
            #        if (np.random.binomial(1, 0.1) == 1):
            #            if (graph.has_edge(lavoratore,lavoratore_next) == False and lavoratore != lavoratore_next):graph.add_edge(lavoratore,lavoratore_next)

    #Cleanup unneeded local variables
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

    #Graph should already be free of self loops
    print("Removing self edges...")
    graph.remove_edges_from(nx.selfloop_edges(graph))

    #Graph should already be undirected
    #print("Converting to undirected graph...")
    #graph = nx.convert_node_labels_to_integers(graph.to_undirected())

    print("total nodes:",len(graph.nodes()))
    print("total edges:",len(graph.edges()))

    #This turns UUIDs to sequential IDs
    relabeled = nx.convert_node_labels_to_integers(graph)
    del(graph)

    #print("Generating GraphML...")
    #nx.write_gml(relabeled, "dataset.gml")
    #print("Generating adjacency list...")
    #nx.write_adjlist(relabeled, "dataset.adjlist")
    #print("Generating GPickle graph...")
    #nx.write_gpickle(relabeled, "Datasets/dataset.gpickle")

    print("Done.")
    return relabeled

if __name__ == "__main__":
    main()