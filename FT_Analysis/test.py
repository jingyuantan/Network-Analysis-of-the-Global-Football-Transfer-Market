import networkx as nx
from flask import session
from sqlalchemy import *
from app import db
from app.models import Player, Transfer, Club, League
import pandas as pd

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

# import things
from flask_table import Table, Col
from sqlalchemy import func

#test = db.session.query(Transfer.fromId, func.count(Transfer.fromId)).group_by(Transfer.fromId).all()
#print(test[1][1])

"""df = pd.DataFrame(columns=['name', 'in', 'out', 'total'])
df.set_index('name')
list_a = ['Liverpool', 'Chelsea', 'Arsenal', 'Liverpool']

for a in list_a:
    if a in df['name']:
        print(a)
        df['in'][a] += 1
        df['total'][a] += 1
    else:
        print('no' + a)
        df.loc[a] = [a, 26, 2, 28]

print(df['in']['Liverpool'])
print(df)"""

G = nx.Graph()
leagueid = 'premier-leaguetransferswettbewerbGB1'
country = 'all'
transfers = Transfer.query.all()
pair_clubs = []

for transfer in transfers:
    clubFrom = Club.query.filter_by(id=transfer.fromId).first()
    clubTo = Club.query.filter_by(id=transfer.toId).first()
    value = transfer.value
    country_from = clubFrom.country
    country_to = clubTo.country

    if leagueid != 'all':
        if clubFrom.leagueId != leagueid or clubTo.leagueId != leagueid:
            continue

    if country != 'all':
        if country_from != country or country_to != country:
            continue

    if value[-1] == 'k':
        value = float(value[1:-1]) / 1000
    else:
        value = float(value[1:-1])

    pair = [clubFrom.name, clubTo.name, value, transfer.fromId, transfer.toId]
    pair_clubs.append(pair)

if pair_clubs:
    df = pd.DataFrame(pair_clubs, columns=['From', 'To', 'Value', 'From Id', 'To Id'])

else:
    data = {'From': ['Invalid Filter'],
            'To': ['Invalid Filter'],
            'Value': [500],
            'From Id': '-',
            'To Id': '-'
            }

    df = pd.DataFrame(data, columns=['From', 'To', 'Value', 'From Id', 'To Id'])

"""df["Occ"] = df.groupby(['From', 'To']).cumcount() + 1
df['Total_Value'] = df.groupby(['From', 'To'])['Value'].cumsum()
df = df.sort_values(by=['Total_Value'])"""

for i in range(len(df)):
    f = df["From"][i]
    t = df["To"][i]
    # p = df["Total_Value"][i]
    G.add_node(f, ids=df['From Id'][i])
    G.add_node(t, ids=df['To Id'][i])
    G.add_edge(f, t)
    # G.add_weighted_edges_from([(f, t, p)])

"""for node in G.nodes():
    clubId = G.nodes[node]['id']
    print(clubId)"""
print(G.number_of_nodes())
print(list(G.nodes))


print(G.nodes["Liverpool"]['ids'])
