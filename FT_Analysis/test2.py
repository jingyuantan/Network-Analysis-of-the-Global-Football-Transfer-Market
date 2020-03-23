from datetime import datetime

import networkx as nx
import pandas as pd
from app.models import Transfer, Club, Player

df_table = pd.DataFrame(columns=['player_nationality', 'destination', 'total_transfer'])
transfers = Transfer.query.all()
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