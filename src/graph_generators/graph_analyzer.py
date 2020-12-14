import networkit as nk
import networkx as nx
import graph_tool as gt

gmlReader = nk.graphio.GMLGraphReader()
G = gmlReader.read("dataset.gml")
print(G.numberOfNodes())
print(G.numberOfEdges())


#graph = gt.load_graph("dataset.gml")
#print(len(graph.get_vertices()))
#print(len(graph.get_edges()))

#G = nx.read_gml('dataset.gml', label='id')
#print(len(G.nodes()))
#print(len(G.edges()))