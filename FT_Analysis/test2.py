from datetime import datetime

import networkx as nx
import pandas as pd
from app.models import Transfer, Club, Player, League

#df = pd.DataFrame(columns=['from', 'to'])
leagueid = 'premier-leaguetransferswettbewerbGB1'
transfers = Transfer.query.all()

clubs = []
leagues = []
countries =[]

for transfer in transfers:
    clubFrom = Club.query.filter_by(id=transfer.fromId).first()
    clubTo = Club.query.filter_by(id=transfer.toId).first()
    LeagueFrom = League.query.filter_by(id=clubFrom.leagueId).first()
    LeagueTo = League.query.filter_by(id=clubTo.leagueId).first()

    if clubFrom.leagueId != leagueid or clubTo.leagueId != leagueid:
        continue

    temp = [clubFrom.name, clubTo.name]
    clubs.append(temp)

df = pd.DataFrame(clubs, columns=['From', 'To'])
plclubs= Club.query.filter_by(leagueId=leagueid)

numer = 0
denom = 0
for i in range(len(df)):
    x = df['From'][i]
    y = df['To'][i]
    denom += 1
    if not df.loc[(df['From'] == y) & (df['To'] == x)].empty:
        numer += 1


print(len(df))
print(numer)
print(denom)
print(numer/denom)









"""df_table = pd.DataFrame(columns=['player_nationality', 'destination', 'total_transfer'])
transfers = Transfer.query.all()
clubs = Club.query.all()
players = Player.query.all()
leagues = League.query.all()
nationality = 'Brazil'
s17_18 = []
s18_19 = []
s19_20 = []
pair_playerCountry = []

for transfer in transfers:
    clubFrom = Club.query.filter_by(id=transfer.fromId).first()
    clubTo = Club.query.filter_by(id=transfer.toId).first()
    value = transfer.value
    country_to = clubTo.country
    player_position = Player.query.filter_by(id=transfer.playerId).first().position
    player_nationality = Player.query.filter_by(id=transfer.playerId).first().nationality
    player_age = Player.query.filter_by(id=transfer.playerId).first().age
    date = datetime.utcfromtimestamp(int(transfer.timestamp)).strftime('%Y-%m-%d')

    if nationality != 'all':
        if player_nationality != nationality:
            continue

    if not df_table.loc[(df_table['player_nationality'] == player_nationality) & (df_table['destination'] == country_to)].empty:
        df_table.loc[(df_table['player_nationality'] == player_nationality) & (df_table['destination'] == country_to), 'total_transfer'] += 1
    else:
        temp_df = pd.DataFrame([[player_nationality, country_to, 1]], columns=['player_nationality', 'destination', 'total_transfer'])
        df_table = pd.concat([df_table, temp_df])

print(df_table)
asd = df_table.to_dict(orient='records')
print(asd)
print("Transfers: " + str(len(transfers)))
print("Clubs: " + str(len(clubs)))
print("Players: " + str(len(players)))
print("Leagues: " + str(len(leagues)))"""
