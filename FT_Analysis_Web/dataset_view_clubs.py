import pandas as pd

df = pd.read_json('dataset/transfers-2018_19-20191004.json', lines=True)
count = 0
arr = []
exist = False

for i in range(len(df)):
    club_from = df["from"][i]["name"]
    club_to = df["to"][i]["name"]

    # clean club_from data
    if club_from == "":
        continue
    if club_from[:1] == " ":
        club_from = club_from[1:]
    if club_from[-3:-2] == 'U':
        club_from = club_from[:-4]

    arr.append(club_from)

    # clean club_to data
    if club_to == '':
        continue
    if club_to[:1] == " ":
        club_to = club_to[1:]
    if club_to[-3:-2] == 'U':
        club_to = club_to[:-4]

    arr.append(club_to)

my_list = list(dict.fromkeys(arr))
my_list.sort()
my_list.pop(0)
print(my_list)
print(len(my_list))

result_file = open("dataset/club_list.csv", "w", encoding='utf-8')
for r in my_list:
    result_file.write(r + "\n")
result_file.close()

result_file = open("dataset/club_list.txt", "w", encoding='utf-8')
for r in my_list:
    result_file.write(r + "\n")
result_file.close()