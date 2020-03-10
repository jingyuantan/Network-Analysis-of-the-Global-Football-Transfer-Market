from datetime import datetime

import networkx as nx
import pandas as pd
from app.models import Transfer, Club, Player

G = nx.Graph()
leagueid = 'premier-leaguetransferswettbewerbGB1'
transfers = Transfer.query.all()
pair_clubs = []
df_table = pd.DataFrame(columns=['name', 'transfer_in', 'transfer_out', 'total_transfer', 'spent', 'received', 'net'])
for transfer in transfers:
    clubFrom = Club.query.filter_by(id=transfer.fromId).first()
    clubTo = Club.query.filter_by(id=transfer.toId).first()
    value = transfer.value
    country_from = clubFrom.country
    country_to = clubTo.country
    player_position = Player.query.filter_by(id=transfer.playerId).first().position
    player_nationality = Player.query.filter_by(id=transfer.playerId).first().nationality
    player_age = Player.query.filter_by(id=transfer.playerId).first().age
    date = datetime.utcfromtimestamp(int(transfer.timestamp)).strftime('%Y-%m-%d')

    if leagueid != 'all':
        if clubFrom.leagueId != leagueid or clubTo.leagueId != leagueid:
            continue

    if value[-1] == 'k':
        value = float(value[1:-1]) / 1000
    else:
        value = float(value[1:-1])

    pair = [clubFrom.name, clubTo.name, value, transfer.fromId, transfer.toId]
    pair_clubs.append(pair)
    df = pd.DataFrame(pair_clubs, columns=['From', 'To', 'Value', 'From Id', 'To Id'])

    for i in range(len(df)):
        f = df["From"][i]
        t = df["To"][i]
        # p = df["Total_Value"][i]
        G.add_node(f, id=df['From Id'][i])
        G.add_node(t, id=df['To Id'][i])
        G.add_edge(f, t)

"""print(nx.betweenness_centrality(G))
print(nx.closeness_centrality(G))
print(nx.eigenvector_centrality(G))
print(G.number_of_nodes())
for node in G.degree:
    print(node[0], " + ", node[1])"""

bet = nx.betweenness_centrality(G)
for a in bet:
    print(a, " + ", bet[a])
