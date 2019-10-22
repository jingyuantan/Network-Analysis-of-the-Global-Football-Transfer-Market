import pandas as pd

df = pd.read_json('dataset/transfers-2018_19-20191004.json', lines=True)
pair_clubs = []
englishPremierLeague_ID = "premier-leaguetransferswettbewerbGB1"
for i in range(len(df)):
    league_from = df["from"][i]["leagueId"]
    league_to = df["to"][i]["leagueId"]

    if league_from != englishPremierLeague_ID or league_to != englishPremierLeague_ID:
        continue
    else:
        pair = [df["from"][i]["name"], df["to"][i]["name"]]
        pair_clubs.append(pair)

print(pair_clubs)
