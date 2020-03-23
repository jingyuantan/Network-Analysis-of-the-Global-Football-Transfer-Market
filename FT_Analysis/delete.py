from app import db
from app.models import Player, League, Transfer, Club
# User is the name of table that has a column name
transfer = Transfer.query.all()
player = Player.query.all()
league = League.query.all()
club = Club.query.all()

for user in transfer:
    #print(user.name)
    db.session.delete(user)

for user in player:
    db.session.delete(user)

for user in league:
    db.session.delete(user)

for user in club:
    db.session.delete(user)

db.session.commit()
#u = User.query.get(1)
#p = Post(body='my first post!', author=u)
#db.session.add(p)
#db.session.commit()