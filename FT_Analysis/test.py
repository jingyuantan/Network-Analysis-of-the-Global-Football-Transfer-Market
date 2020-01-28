from flask import session
from sqlalchemy import *
from app import db
from app.models import Player, Transfer, Club, League
import pandas as pd

import re
"""
test = re.compile('U[0-9][0-9]')

asd = "Liverpool U23"
#print(test.match(asd[-3:]))
print(test.match(asd[-3:-1]))

if test.match(asd[-3:]):
    print("asd")
else:
    print("qwer")
"""

# import things
from flask_table import Table, Col
from sqlalchemy import func

#test = db.session.query(Transfer.fromId, func.count(Transfer.fromId)).group_by(Transfer.fromId).all()
#print(test[1][1])

df = pd.DataFrame(columns=['name', 'in', 'out', 'total'])
df.set_index('name')
list_a = ['Liverpool', 'Chelsea', 'Arsenal', 'Liverpool']

for a in list_a:
    if a in df['name']:
        print(a)
        df['in'][a] += 1
        df['total'][a] += 1
    else:
        print('no' + a)
        df.loc[a] = [a, 26, 2, 28]

print(df)

