import pandas as pd

df = pd.read_json('data/transfers-2018_19-20191004.json', lines=True)
count = 0
arr = []
exist = False
englishPremierLeague_ID = "premier-leaguetransferswettbewerbGB1"


for i in range(len(df)):
    league_from = df["from"][i]["leagueId"]
    league_to = df["to"][i]["leagueId"]

    if league_from != "":
        arr.append(league_from)

    if league_to != "":
        arr.append(league_to)

my_list = list(dict.fromkeys(arr))
my_list.sort()
print(my_list)
print(len(my_list))

result_file = open("data/leagueId_list.csv", "w", encoding='utf-8')
for r in my_list:
    result_file.write(r + "\n")
result_file.close()

result_file = open("data/leagueId_list.txt", "w", encoding='utf-8')
for r in my_list:
    result_file.write(r + "\n")
result_file.close()
