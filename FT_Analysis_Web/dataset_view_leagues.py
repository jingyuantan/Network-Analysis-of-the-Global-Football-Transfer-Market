import pandas as pd

df = pd.read_json('dataset/transfers-2018_19-20191004.json', lines=True)
count = 0
arr = []
exist = False

for i in range(len(df)):
    league_from = df["from"][i]["league"]
    league_to = df["to"][i]["league"]

    if league_from == "":
        continue
    arr.append(league_from)

    if league_to == '':
        continue
    arr.append(league_to)

my_list = list(dict.fromkeys(arr))
my_list.sort()
print(my_list)
print(len(my_list))

result_file = open("dataset/league_list.csv", "w", encoding='utf-8')
for r in my_list:
    result_file.write(r + "\n")
result_file.close()

result_file = open("dataset/league_list.txt", "w", encoding='utf-8')
for r in my_list:
    result_file.write(r + "\n")
result_file.close()
