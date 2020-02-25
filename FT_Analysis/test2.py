"""from datetime import datetime
ts = int("1548028800")
ts2 = int('1530399600')
# if you encounter a "year is out of range" error the timestamp
# may be in milliseconds, try `ts /= 1000` in that case
print(datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d'))
print(datetime.utcfromtimestamp(ts2).strftime('%Y-%m-%d'))
date1 = datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d')
date2 = datetime.utcfromtimestamp(ts2).strftime('%Y-%m-%d')
# ts is 2019
# ts2 is 2018
# ts > ts2 = true
print(date1 > date2)
print(type(date1))
# this format
date3 = '2020-02-05'
print('2'<'2.5')"""
from datetime import datetime

from app.models import Transfer, Club, Player
from sqlalchemy import or_, and_
import json
import pandas as pd
transfers = Transfer.query.all()
season = 'all'
leagueid = 'premier-leaguetransferswettbewerbGB1'
country = 'all'
position = 'all'
nationality = 'all'
ageFrom = ''
ageTo = ''
valueFrom = ''
valueTo = ''
dateFrom = ''
dateTo = ''
pair_clubs = []
s17_18 = []
s18_19 = []
s19_20 = []

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

    if country != 'all':
        if country_from != country or country_to != country:
            continue

    if position != 'all':
        if player_position != position:
            continue

    if nationality != 'all':
        if player_nationality != nationality:
            continue

    if ageFrom != '':
        if player_age < ageFrom:
            continue

    if ageTo != '':
        if player_age > ageTo:
            continue

    if value[-1] == 'k':
        value = float(value[1:-1]) / 1000
    else:
        value = float(value[1:-1])

    if valueFrom != '':
        if value < float(valueFrom):
            continue

    if valueTo != '':
        if value > float(valueTo):
            continue

    temp = [clubFrom.name, clubTo.name, value]
    if transfer.season == '2017/2018':
        print(transfer.season + "aaa")
        s17_18.append(temp)
    elif transfer.season == '2018/2019':
        print(transfer.season + "bbb")
        s18_19.append(temp)
    elif transfer.season == '2019/2020':
        print(transfer.season + "ccc")
        s19_20.append(temp)

    if dateFrom != '':
        if date < dateFrom:
            continue

    if dateTo != '':
        if date > dateTo:
            continue

    if season != 'all':
        if transfer.season != season:
            continue

    pair = [clubFrom.name, clubTo.name, value]
    pair_clubs.append(pair)

if pair_clubs:
    df = pd.DataFrame(pair_clubs, columns=['From', 'To', 'Value'])
else:
    data = {'From': ['Invalid Filter'],
            'To': ['Invalid Filter'],
            'Value': [500],
            'From Id': '-',
            'To Id': '-'
            }
    df = pd.DataFrame(data, columns=['From', 'To', 'Value'])

if s17_18:
    df17_18 = pd.DataFrame(pair_clubs, columns=['From', 'To', 'Value'])
else:
    data = {'From': ['Invalid Filter'],
            'To': ['Invalid Filter'],
            'Value': [500],
            'From Id': '-',
            'To Id': '-'
            }
    df17_18 = pd.DataFrame(data, columns=['From', 'To', 'Value'])

if s18_19:
    df18_19 = pd.DataFrame(pair_clubs, columns=['From', 'To', 'Value'])
else:
    data = {'From': ['Invalid Filter'],
            'To': ['Invalid Filter'],
            'Value': [500],
            'From Id': '-',
            'To Id': '-'
            }
    df18_19 = pd.DataFrame(data, columns=['From', 'To', 'Value'])

if s19_20:
    df19_20 = pd.DataFrame(pair_clubs, columns=['From', 'To', 'Value'])
else:
    data = {'From': ['Invalid Filter'],
            'To': ['Invalid Filter'],
            'Value': [500],
            'From Id': '-',
            'To Id': '-'
            }
    df19_20 = pd.DataFrame(data, columns=['From', 'To', 'Value'])

print(df)
print(df19_20)
print(df18_19)
print(df17_18)