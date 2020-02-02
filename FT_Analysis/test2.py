import networkx as nx
G = nx.Graph()

G.add_node('abc', dob=1185, pob='usa', dayob='monday')

print(G.nodes['abc']['dob'] )# 1185
print(G.nodes['abc']['pob']) # usa
print(G.nodes['abc']['dayob']) # monday