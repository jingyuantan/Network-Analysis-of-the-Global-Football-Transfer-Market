from app import db


class Player(db.Model):
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String)
    position = db.Column(db.String)
    age = db.Column(db.String)
    nationality = db.Column(db.String)
    img_href = db.Column(db.String)
    transfers = db.relationship('Transfer', backref='player', lazy='dynamic')

    def __repr__(self):
        return '<Player {}>'.format(self.name)


class Club(db.Model):
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, index=True)
    country = db.Column(db.String)
    leagueId = db.Column(db.String, db.ForeignKey('league.id'))
    country_img_href = db.Column(db.String, index=True)
    club_img_href = db.Column(db.String, index=True)

    def __repr__(self):
        return '<Club {}>'.format(self.name)


class League(db.Model):
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, index=True)
    href = db.Column(db.String, index=True)
    clubs = db.relationship('Club', backref='league', lazy='dynamic')
    country = db.Column(db.String)

    def __repr__(self):
        return '<League {}>'.format(self.name)


class Transfer(db.Model):
    id = db.Column(db.String, primary_key=True)
    playerId = db.Column(db.String, db.ForeignKey('player.id'))
    fromId = db.Column(db.String, db.ForeignKey('club.id'))
    toId = db.Column(db.String, db.ForeignKey('club.id'))
    fromLeagueId = db.Column(db.String, db.ForeignKey('league.id'))
    toLeagueId = db.Column(db.String, db.ForeignKey('league.id'))
    fromCountry = db.Column(db.String)
    toCountry = db.Column(db.String)
    value = db.Column(db.String)
    timestamp = db.Column(db.String)
    season = db.Column(db.String)
    fromClubs = db.relationship('Club', foreign_keys=[fromId])
    toClubs = db.relationship('Club', foreign_keys=[toId])
    fromLeagues = db.relationship('League', foreign_keys=[fromLeagueId])
    toLeagues = db.relationship('League', foreign_keys=[toLeagueId])

    def __repr__(self):
        return '<Transfer {}>'.format(self.id)

