from sqlalchemy import *
from app import db
from app.models import Player, Transfer, Club
transfers = Transfer.query.all()
import re
"""
test = re.compile('U[0-9][0-9]')

asd = "Liverpool U23"
#print(test.match(asd[-3:]))
print(test.match(asd[-3:-1]))

if test.match(asd[-3:]):
    print("asd")
else:
    print("qwer")
"""

import plotly.graph_objects as go

import networkx as nx

G = nx.random_geometric_graph(200, 0.125)
edge_x = []
edge_y = []
for edge in G.edges():
    x0, y0 = G.nodes[edge[0]]['pos']
    x1, y1 = G.nodes[edge[1]]['pos']
    print(G.nodes[edge[0]]['pos'])
    print(G.nodes[edge[1]]['pos'])