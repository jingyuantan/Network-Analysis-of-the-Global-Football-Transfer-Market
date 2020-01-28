from app import db
from app.models import Player, League, Transfer, Club
# User is the name of table that has a column name
users = Transfer.query.all()

for user in users:
    #print(user.name)
    db.session.delete(user)

db.session.commit()
#u = User.query.get(1)
#p = Post(body='my first post!', author=u)
#db.session.add(p)
#db.session.commit()