import pandas as pd

from app.models import Transfer, Player, Club, League

"""df = pd.read_json("data/transfers-20200418.json", lines=True)
# 41176 records in total
# 41117 players
# 10189 clubs
# 178 countries
# 392 leagues

# transfer: 140996 
# player: 82423
# club: 16347
# country: 189
# league: 411

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

player = []
club = []
country = []
league = []
n = 0
transfers = Transfer.query.all()
for transfer in transfers:
    player.append(transfer.playerId)
    club.append(transfer.fromId)
    club.append(transfer.toId)
    country.append(transfer.fromCountry)
    country.append(transfer.toCountry)
    league.append(transfer.fromLeagueId)
    league.append(transfer.toLeagueId)
    n += 1

player = sorted(list(dict.fromkeys(player)), key=str)
club = sorted(list(dict.fromkeys(club)), key=str)
country = sorted(list(dict.fromkeys(country)), key=str)
league = sorted(list(dict.fromkeys(league)), key=str)

print("player: " + str(len(player)))
print("club: " + str(len(club)))
print("country: " + str(len(country)))
print("league: " + str(len(league)))
print("transfer:" + str(n))

# player: 5065
# club: 1526
# country: 90
# league: 211
# transfer:5755