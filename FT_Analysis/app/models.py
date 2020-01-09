from app import db


class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    position = db.Column(db.String(64))
    age = db.Column(db.Integer)
    nationality = db.Column(db.String(64))
    href = db.Column(db.String(200), index=True, unique=True)
    img_href = db.Column(db.String(200), index=True, unique=True)
    transfers = db.relationship('Transfer', backref='player', lazy='dynamic')

    def __repr__(self):
        return '<Player {}>'.format(self.name)


class Club(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    country = db.Column(db.String(64))
    leagueId = db.Column(db.String(64), db.ForeignKey('league.id'))
    country_img_href = db.Column(db.String(200), index=True, unique=True)
    club_img_href = db.Column(db.String(200), index=True, unique=True)
    transfers = db.relationship('Transfer', backref='club', lazy='dynamic')

    def __repr__(self):
        return '<Club {}>'.format(self.name)


class League(db.Model):
    id = db.Column(db.String(200), primary_key=True)
    name = db.Column(db.String(64), index=True)
    href = db.Column(db.String(200), index=True, unique=True)
    clubs = db.relationship('Club', backref='league', lazy='dynamic')

    def __repr__(self):
        return '<League {}>'.format(self.name)


class Transfer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    playerId = db.Column(db.Integer, db.ForeignKey('player.id'))
    fromId = db.Column(db.Integer, db.ForeignKey('club.id'))
    toId = db.Column(db.Integer, db.ForeignKey('club.id'))
    href = db.Column(db.String(200), unique=True)
    value = db.Column(db.String(64))
    timestamp = db.Column(db.String(64))
    season = db.Column(db.String(64))

    def __repr__(self):
        return '<Transfer {}>'.format(self.id)

