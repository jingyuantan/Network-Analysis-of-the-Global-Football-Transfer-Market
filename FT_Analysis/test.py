"""import pandas as pd

df = pd.read_json("data/transfers-20200131.json", lines=True)
# 41176 records in total
# 41117 players
# 10189 clubs
# 178 countries
# 392 leagues

player = []
club = []
country = []
league = []

for i in range(len(df)):
    player.append(df["player"][i]["href"])
    club.append(df["from"][i]["href"])
    club.append(df["to"][i]["href"])
    country.append(df["from"][i]["country"])
    country.append(df["to"][i]["country"])
    league.append(df["from"][i]["leagueId"])
    league.append(df["to"][i]["leagueId"])

player = sorted(list(dict.fromkeys(player)), key=str)
club = sorted(list(dict.fromkeys(club)), key=str)
country = sorted(list(dict.fromkeys(country)), key=str)
league = sorted(list(dict.fromkeys(league)), key=str)

print("player: " + str(len(player)))
print("club: " + str(len(club)))
print("country: " + str(len(country)))
print("league: " + str(len(league)))"""
for z in range(6):
    print(z)